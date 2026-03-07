<?php
// Telegram bot tokeni
define('BOT_TOKEN', '8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o');
define('API_URL', 'https://api.telegram.org/bot' . BOT_TOKEN . '/');

// PRO foydalanuvchilar ID ro'yxati
$pro_users = [123456789, 987654321]; // Pro sotib olgan ID larni shu yerga yozing

// Bot username-ni avtomatik aniqlash
$me = json_decode(file_get_contents(API_URL . "getMe"), true);
$bot_username = '@' . $me['result']['username'];

// Shartnoma matni
$contract_text = "Soxta Chek Bot shartnomasi:\n\n1. Foydalanuvchi soxta chek yasash xizmatidan qonuniy maqsadda foydalanishni kafolatlaydi.\n2. Botda ko‘rsatilgan ma'lumotlarning to‘g‘riligi uchun javobgarlik foydalanuvchida.\n3. Bot ishlab chiquvchisi nojo‘ya foydalanish uchun mas’ul emas.\n\nShartnomani qabul qilsangiz, «Qabul qilaman» tugmasini bosing.";

// Xabar yuborish funksiyasi
function sendMessage($chat_id, $text, $reply_markup = null) {
    $data = [
        'chat_id' => $chat_id,
        'text' => $text,
        'parse_mode' => 'HTML',
    ];
    if ($reply_markup) {
        $data['reply_markup'] = json_encode($reply_markup);
    }
    file_get_contents(API_URL . "sendMessage?" . http_build_query($data));
}

// Inline tugma generatori
function getInlineKeyboard($buttons) {
    return ['inline_keyboard' => $buttons];
}

// Kiruvchi ma'lumotlar
$content = file_get_contents("php://input");
$update = json_decode($content, true);

if (!$update) exit;

$chat_id = $update['message']['chat']['id'] ?? $update['callback_query']['message']['chat']['id'] ?? null;
$user_id = $update['message']['from']['id'] ?? $update['callback_query']['from']['id'] ?? null;
$message = $update['message']['text'] ?? null;
$callback_data = $update['callback_query']['data'] ?? null;

if ($message == '/start') {
    $keyboard = getInlineKeyboard([
        [['text' => 'Qabul qilaman', 'callback_data' => 'contract_accept']],
        [['text' => 'Qabul qilmayman', 'callback_data' => 'contract_decline']]
    ]);
    sendMessage($chat_id, $contract_text, $keyboard);
    exit;
}

if ($callback_data == 'contract_accept') {
    if (in_array($user_id, $pro_users)) {
        $keyboard = getInlineKeyboard([
            [['text' => 'Paynet Chek', 'callback_data' => 'choose_paynet']]
        ]);
        sendMessage($chat_id, "Shartnoma qabul qilindi.\n\nIltimos, ilovani tanlang:", $keyboard);
    } else {
        sendMessage($chat_id, "Siz PRO foydalanuvchi emassiz.\nChek yasash uchun @Dalishev_coder ga murojaat qiling.");
    }
    exit;
}

if ($callback_data == 'contract_decline') {
    sendMessage($chat_id, "Siz shartnomani qabul qilmagansiz.\nChek yasash mumkin emas.");
    exit;
}

if ($callback_data == 'choose_paynet') {
    sendMessage($chat_id, "Paynet tanlandi.\n\nQuyidagi formatda yuboring:\n\n40000\nIsm Familiya\n8600123456789012\n10:01");
    file_put_contents("waiting_{$user_id}.txt", "paynet");
    exit;
}

if ($message && file_exists("waiting_{$user_id}.txt")) {
    $state = file_get_contents("waiting_{$user_id}.txt");
    $lines = explode("\n", trim($message));
    if (count($lines) != 4) {
        sendMessage($chat_id, "Noto‘g‘ri format.\n\nMasalan:\n40000\nIsm Familiya\n8600123456789012\n10:01");
        exit;
    }

    list($summa, $name, $card, $time) = $lines;

    if (!is_numeric(str_replace(' ', '', $summa))) {
        sendMessage($chat_id, "Summa noto‘g‘ri.");
        exit;
    }
    if (!preg_match('/^\d{12,19}$/', $card)) {
        sendMessage($chat_id, "Karta raqami xato.");
        exit;
    }
    if (!preg_match('/^\d{2}:\d{2}$/', $time)) {
        sendMessage($chat_id, "Vaqt xato (HH:MM formatda).");
        exit;
    }

    $summa_api = urlencode(trim($summa));
    $name_api = urlencode(trim($name));
    $card_api = trim($card);
    $time_api = trim($time);

    // API orqali rasm olish
    $api_url = "={$card_api}&ism={$name_api}&summa={$summa_api}&soat={$time_api}"; // Api url qoying boshiga va api toʻgʻriligiga ishonch hosil qiling!

    // Chek rasm yuborish
    $send_photo_url = API_URL . "sendPhoto";
    $post_fields = [
        'chat_id' => $chat_id,
        'caption' => "Chek {$bot_username} orqali yaratildi✅",
        'photo' => $api_url
    ];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_HTTPHEADER, ["Content-Type:multipart/form-data"]);
    curl_setopt($ch, CURLOPT_URL, $send_photo_url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post_fields);
    curl_exec($ch);
    curl_close($ch);

    unlink("waiting_{$user_id}.txt");
    exit;
}
?>
