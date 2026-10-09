<?php
// Extera enquiry form handler. Used by the contact and support forms.
// Upload to the web root next to the HTML files. Needs PHP 7.4+ and a working mail() on the host.

const TO_ADDRESS = 'customer.services@extera.co.uk';
const FROM_ADDRESS = 'website@extera.co.uk';   // must be an address on your own domain so mail is not marked as spam
const SUBJECT_PREFIX = 'Website enquiry';
const MAX_PER_HOUR = 5;                         // submissions allowed per visitor IP per hour
const DRY_RUN = false;                          // true writes to sent-test.log instead of sending (for local testing)

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: contact.html');
    exit;
}

function clean(string $v, int $max): string {
    $v = trim(str_replace(["\r", "\0"], '', $v));
    return mb_substr($v, 0, $max);
}
function oneline(string $v): string {
    return preg_replace('/[\r\n]+/', ' ', $v);
}
function fail(string $message, int $code = 400): void {
    http_response_code($code);
    header('Content-Type: text/html; charset=utf-8');
    $m = htmlspecialchars($message, ENT_QUOTES);
    echo '<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
        . '<meta name="robots" content="noindex"><title>Message not sent | Extera</title>'
        . '<style>body{font:16px/1.6 "Open Sans",Arial,sans-serif;max-width:560px;margin:15vh auto;padding:0 16px;color:#334155}a{color:#155f99}</style></head>'
        . '<body><h1 style="font-size:1.5rem">Sorry, your message was not sent</h1><p>' . $m . '</p>'
        . '<p><a href="javascript:history.back()">Go back and try again</a>, or call us on <a href="tel:01295220600">01295 220 600</a>.</p></body></html>';
    exit;
}

// Honeypot: real visitors never see or fill this field.
if (!empty($_POST['website'])) {
    header('Location: thanks.html');
    exit;
}

// Simple per-IP rate limit.
$ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
$store = sys_get_temp_dir() . '/extera-form-' . md5($ip) . '.json';
$now = time();
$hits = [];
if (is_file($store)) {
    $hits = array_filter(json_decode((string) file_get_contents($store), true) ?: [], fn($t) => $t > $now - 3600);
}
if (count($hits) >= MAX_PER_HOUR) {
    fail('Too many messages from this connection. Please try again later or call us.', 429);
}

$form = ($_POST['form'] ?? '') === 'support' ? 'Support request' : 'Quote request';
$name = clean($_POST['name'] ?? '', 120);
$company = clean($_POST['company'] ?? '', 160);
$email = clean($_POST['email'] ?? '', 200);
$phone = clean($_POST['phone'] ?? '', 40);
$interest = clean($_POST['interest'] ?? '', 80);
$message = clean($_POST['message'] ?? '', 5000);

foreach (['name', 'company', 'email', 'phone', 'interest'] as $f) { $$f = oneline($$f); }

if ($name === '') fail('Please enter your name.');
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) fail('Please enter a valid email address.');
if ($phone !== '' && !preg_match('/^[0-9 +()\-.]{6,40}$/', $phone)) fail('Please check your phone number.');
// Block links-only spam: many URLs in a message is almost always junk.
if (preg_match_all('~https?://~i', $message) > 2) fail('Please remove the links from your message.');

$lines = [
    "Form:     $form",
    "Name:     $name",
    "Company:  " . ($company ?: '-'),
    "Email:    $email",
    "Phone:    " . ($phone ?: '-'),
];
if ($interest !== '') $lines[] = "Interest: $interest";
$lines[] = '';
$lines[] = 'Message:';
$lines[] = $message ?: '(none)';
$lines[] = '';
$lines[] = "Sent from the website at " . date('d M Y H:i') . " (IP $ip)";
$body = implode("\n", $lines);

$subject = '=?UTF-8?B?' . base64_encode(SUBJECT_PREFIX . ' - ' . $form . ': ' . oneline($name)) . '?=';
$headers = [
    'From: Extera website <' . FROM_ADDRESS . '>',
    'Reply-To: ' . $email,
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'X-Mailer: PHP/' . phpversion(),
];

if (DRY_RUN) {
    file_put_contents(__DIR__ . '/sent-test.log', "To: " . TO_ADDRESS . "\nSubject: $subject\n" . implode("\n", $headers) . "\n\n$body\n\n----\n", FILE_APPEND);
    $sent = true;
} else {
    $sent = mail(TO_ADDRESS, $subject, $body, implode("\r\n", $headers), '-f' . FROM_ADDRESS);
}
if (!$sent) {
    fail('We could not send your message just now. Please call us or email ' . TO_ADDRESS . '.', 500);
}

$hits[] = $now;
file_put_contents($store, json_encode(array_values($hits)));
header('Location: thanks.html');
exit;
