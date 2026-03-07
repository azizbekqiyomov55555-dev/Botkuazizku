<?php
define('API_KEY',"8745440078:AAFBIYJw_BplZeK0jYRjJkwM0oTVyHrJ99o");  

$admin = "8537782289";

function bot($method,$datas=[]){
$url = "https://api.telegram.org/bot".API_KEY."/".$method;
$ch = curl_init();
curl_setopt($ch,CURLOPT_URL,$url);
curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
curl_setopt($ch,CURLOPT_POSTFIELDS,$datas);
$res = curl_exec($ch);
if(curl_error($ch)){
var_dump(curl_error($ch));
}else{
return json_decode($res);
}}

function hisob(){
$text = "🏆 TOP10 = Hisoblar\n\n";
$daten = [];
$rev = [];
$fayllar = glob("foydalanuvchi/hisob/*.*");
foreach($fayllar as $file){
if(mb_stripos($file,".txt")!==false){
$value = file_get_contents($file);
$id = str_replace(["foydalanuvchi/hisob/",".txt"],["",""],$file);
$daten[$value] = $id;
$rev[$id] = $value;
}
echo $file;
}
asort($rev);
$reversed = array_reverse($rev);
for($i=0;$i<10;$i+=1){
$order = $i+1;
$id = $daten["$reversed[$i]"];
$text.= "<b>{$order}</b>. <a href='tg://user?id={$id}'>{$id}</a> - "."<code>".$reversed[$i]."</code>"." <b>so'm</b>"."\n";
}
return $text;
}

function dostlar(){
$text2 = "🏆 TOP10 = Do'stlar\n\n";
$daten2 = [];
$rev2 = [];
$fayllar2 = glob("foydalanuvchi/referal/*.*");
foreach($fayllar2 as $file2){
if(mb_stripos($file2,".txt")!==false){
$value2 = file_get_contents($file2);
$id2 = str_replace(["foydalanuvchi/referal/",".txt"],["",""],$file2);
$daten2[$value2] = $id2;
$rev2[$id2] = $value2;
}
echo $file2;
}
asort($rev2);
$reversed2 = array_reverse($rev2);
for($i2=0;$i2<10;$i2+=1){
$order2 = $i2+1;
$id2 = $daten2["$reversed2[$i2]"];
$text2.= "<b>{$order2}</b>. <a href='tg://user?id={$id2}'>{$id2}</a> - "."<code>".$reversed2[$i2]."</code>"." <b>ta</b>"."\n";
}
return $text2;
}

function deleteFolder($path){
if(is_dir($path) === true){
$files = array_diff(scandir($path), array('.', '..'));
foreach ($files as $file)
deleteFolder(realpath($path) . '/' . $file);
return rmdir($path);
}else if (is_file($path) === true)
return unlink($path);
return false;
}

function joinchat($id){
global $mid;
$array = array("inline_keyboard");
$kanallar=file_get_contents("sozlamalar/kanal/ch.txt");
$ex = explode("\n",$kanallar);
for($i=0;$i<=count($ex) -1;$i++){
$first_line = $ex[$i];
$first_ex = explode("@",$first_line);
$url = $first_ex[1];
$ism=bot('getChat',['chat_id'=>"@".$url,])->result->title;
$ret = bot("getChatMember",[
"chat_id"=>"@$url",
"user_id"=>$id,
]);
$stat = $ret->result->status;
if((($stat=="creator" or $stat=="administrator" or $stat=="member"))){
$array['inline_keyboard']["$i"][0]['text'] = "✅ ". $ism;
$array['inline_keyboard']["$i"][0]['url'] = "https://t.me/$url";
}else{
$array['inline_keyboard']["$i"][0]['text'] = "❌ ". $ism;
$array['inline_keyboard']["$i"][0]['url'] = "https://t.me/$url";
$uns = true;
}}

if($uns == true){
bot("sendMessage",[
"chat_id"=>$id,
"text"=>"<b>⚠️ Botdan foydalanish uchun quyidagi kanalimizga azo bo'ling va /start  bosing!</b>",
"parse_mode"=>"html",
"reply_to_message_id"=>$mid,
"disable_web_page_preview"=>true,
"reply_markup"=>json_encode($array),
]);
return false;
}else{
return true;
}}

$update = json_decode(file_get_contents('php://input'));
$message = $update->message;
$cid = $message->chat->id;
$tx = $message->text;
$mid = $message->message_id;
$name = $message->from->first_name;
$fid = $message->from->id;
$callback = $update->callback_query;
$data = $callback->data;
$callid = $callback->id;
$ccid = $callback->message->chat->id;
$cmid = $callback->message->message_id;
$from_id = $update->message->from->id;
$token = $message->text;
$text = $message->text;
$message_id = $callback->message->message_id;
$data = $update->callback_query->data;
$callcid=$update->callback_query->message->chat->id;
$doc = $update->message->document;
$doc_id = $doc->file_id;
$cqid = $update->callback_query->id;
$callfrid = $update->callback_query->from->id;
$botname = bot('getme',['FastKonsBot'])->result->username;
#-----------------------------
mkdir("foydalanuvchi");
mkdir("foydalanuvchi/sarmoya/$fid");
mkdir("foydalanuvchi/bot/$fid");
mkdir("foydalanuvchi/sarhisob");
mkdir("foydalanuvchi/sarmoya");
mkdir("foydalanuvchi/referal");
mkdir("foydalanuvchi/hisob");
mkdir("sozlamalar/hamyon");
mkdir("sozlamalar/kanal");
mkdir("sozlamalar/tugma");
mkdir("sozlamalar/xizmat");
mkdir("sozlamalar/xizmatlar");
mkdir("sozlamalar/bot");
mkdir("sozlamalar/pul");
mkdir("statistika");
mkdir("nak/$cid");
mkdir("nak");
mkdir("sozlamalar");
mkdir("otkazma");
mkdir("botlar");
mkdir("step");
mkdir("baza");
mkdir("ban");
#-----------------------------

if(!file_exists("foydalanuvchi/hisob/$fid.1.txt")){
file_put_contents("foydalanuvchi/hisob/$fid.1.txt","0");
}
if(!file_exists("foydalanuvchi/hisob/$fid.1txt")){
file_put_contents("foydalanuvchi/hisob/$fid.1txt","0");
}
if(!file_exists("foydalanuvchi/hisob/$fid.txt")){
file_put_contents("foydalanuvchi/hisob/$fid.txt","0");
}
if(!file_exists("foydalanuvchi/sarhisob/$fid.kiritgan")){
file_put_contents("foydalanuvchi/sarhisob/$fid.kiritgan","0");
}
if(!file_exists("foydalanuvchi/sarhisob/$fid.chiqargan")){
file_put_contents("foydalanuvchi/sarhisob/$fid.chiqargan","0");
}
if(!file_exists("foydalanuvchi/referal/$fid.txt")){
file_put_contents("foydalanuvchi/referal/$fid.txt","0");
}
if(!file_exists("foydalanuvchi/sarmoya/$fid/sarson.txt")){  
file_put_contents("foydalanuvchi/sarmoya/$fid/sarson.txt","0");
}
if(!file_exists("sozlamalar/pul/referal.txt")){
file_put_contents("sozlamalar/pul/referal.txt","100");
}
if(!file_exists("sozlamalar/pul/valyuta.txt")){
file_put_contents("sozlamalar/pul/valyuta.txt","so'm");
}
if(!file_exists("sozlamalar/tugma/tugma1.txt")){
file_put_contents("sozlamalar/tugma/tugma1.txt","🤖 Botlarni boshqarish");
}
if(!file_exists("sozlamalar/tugma/tugma2.txt")){
file_put_contents("sozlamalar/tugma/tugma2.txt","🗄 Kabinet");
}
if(!file_exists("sozlamalar/tugma/tugma3.txt")){
file_put_contents("sozlamalar/tugma/tugma3.txt","💵 Pul ishlash");
}
if(!file_exists("sozlamalar/tugma/tugma4.txt")){
file_put_contents("sozlamalar/tugma/tugma4.txt","☎️ Murojaat");
}
if(!file_exists("sozlamalar/tugma/tugma5.txt")){
file_put_contents("sozlamalar/tugma/tugma5.txt","🛒 Bot do'koni");
}
if(!file_exists("sozlamalar/tugma/tugma6.txt")){
file_put_contents("sozlamalar/tugma/tugma6.txt","📦 Buyurtma berish");
}
if(!file_exists("sozlamalar/tugma/tugma7.txt")){
file_put_contents("sozlamalar/tugma/tugma7.txt","🔗 Taklifnoma");
}
if(!file_exists("sozlamalar/kanal/ch.txt")){
file_put_contents("sozlamalar/kanal/ch.txt","@Reliabledev");
}
if(!file_exists("otkazma/$fid.idraqam")){  
file_put_contents("otkazma/$fid.idraqam","");
}
if(!file_exists("otkazma/$fid.pulraqam")){  
file_put_contents("otkazma/$fid.pulraqam","");
}
if(!file_exists("statistika/hammabot.txt")){  
file_put_contents("statistika/hammabot.txt","0");
}
if(!file_exists("statistika/aktivbot.txt")){  
file_put_contents("statistika/aktivbot.txt","0");
}
if(file_get_contents("statistika/obunachi.txt")){
} else{
file_put_contents("statistika/obunachi.txt", "0");
}
if(!file_exists("baza/all.num")){  
file_put_contents("baza/all.num","0");
}

$kiritgan=file_get_contents("foydalanuvchi/hisob/$fid.1.txt");
$odam=file_get_contents("foydalanuvchi/referal/$fid.txt");
$odamcha = file_get_contents("foydalanuvchi/referal/$fid.db");
$asosiy=file_get_contents("foydalanuvchi/hisob/$fid.txt");
$sar=file_get_contents("foydalanuvchi/hisob/$fid.1txt");
$sarson = file_get_contents("foydalanuvchi/sarmoya/$fid/sarson.txt");
$pul = file_get_contents("sozlamalar/pul/valyuta.txt");
$taklifpul = file_get_contents("sozlamalar/pul/referal.txt");
$tugma1 = file_get_contents("sozlamalar/tugma/tugma1.txt");
$tugma2 = file_get_contents("sozlamalar/tugma/tugma2.txt");
$tugma3 = file_get_contents("sozlamalar/tugma/tugma3.txt");
$tugma4 = file_get_contents("sozlamalar/tugma/tugma4.txt");
$tugma5 = file_get_contents("sozlamalar/tugma/tugma5.txt");
$tugma6 = file_get_contents("sozlamalar/tugma/tugma6.txt");
$tugma7 = file_get_contents("sozlamalar/tugma/tugma7.txt");
$kanallar=file_get_contents("sozlamalar/kanal/ch.txt");
#-----------------------------------#
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
$royxat = file_get_contents("sozlamalar/bot/$kategoriya/royxat.txt");
$type = file_get_contents("sozlamalar/bot/$kategoriya/$royxat/turi.txt");
$narx = file_get_contents("sozlamalar/bot/$kategoriya/$royxat/narx.txt");
$tavsif = file_get_contents("sozlamalar/bot/$kategoriya/$royxat/tavsif.txt");
#-----------------------------------#
$kategoriya2 = file_get_contents("sozlamalar/hamyon/kategoriya.txt");
$raqam = file_get_contents("sozlamalar/hamyon/$kategoriya2/raqam.txt");
#-----------------------------------#

$saved = file_get_contents("step/odam.txt");
$num = file_get_contents("baza/all.num");
$ban = file_get_contents("ban/$fid.txt");
$statistika = file_get_contents("statistika/obunachi.txt");
$aktivbot=file_get_contents("statistika/aktivbot.txt");
$hammabot=file_get_contents("statistika/hammabot.txt");
$soat=date("H:i",strtotime("2 hour"));
$referalsum = file_get_contents("foydalanuvchi/hisob/$fid.txt");
$referalid = file_get_contents("foydalanuvchi/referal/$fid.referal");
$referalcid = file_get_contents("foydalanuvchi/referal/$ccid.referal");
$userstep=file_get_contents("step/$fid.txt");
$userstep1=file_get_contents("step/$fid.txt1");

if(mb_stripos($text,"/start $cid")){
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"",
'parse_mode'=>'html',
]);
}else{
$idref = "foydalanuvchi/referal/$ex.db";
$idref2 = file_get_contents($idref);
$id = "$cid\n";
$handle = fopen($idref, 'a+');
fwrite($handle, $id);
fclose($handle);
if(mb_stripos($idref2,$cid) !== false ){
}else{
$pub=explode(" ",$text);
$ex=$pub[1];
$pulim = file_get_contents("foydalanuvchi/hisob/$ex.txt");
$a=$pulim+$taklifpul;
file_put_contents("foydalanuvchi/hisob/$ex.txt","$a");
$odam = file_get_contents("foydalanuvchi/referal/$ex.txt");
$b=$odam+1;
file_put_contents("foydalanuvchi/referal/$ex.txt","$b");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"",
'parse_mode'=>'html',
'reply_markup'=>$main_menu,
]);
bot('SendMessage',[
'chat_id'=>$ex,
'text'=>"<b>📳 Sizda yangi <a href='tg://user?id=$cid'>taklif</a> mavjud!</b>

<i>Hisobingizga $taklifpul $pul qo'shildi!</i>",
'parse_mode'=>'html',
]);
}}

if($tx){
if($ban == "ban"){
exit();
}else{
}}

if($data){
$ban = file_get_contents("ban/$ccid.txt");
if($ban == "ban"){
exit();
}else{
}}

$main_menu = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"$tugma1"]],
[['text'=>"$tugma2"],['text'=>"$tugma3"]],
[['text'=>"$tugma5"],['text'=>"$tugma4"]],
[['text'=>"🛠️ Sozlamalar"]],
]]);

$nak_menu = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"📦 Buyurtma berish"]],
[['text'=>"$tugma2"],['text'=>"$tugma3"]],
[['text'=>"📊 Buyurtma kuzatish"],['text'=>"$tugma4"]],
[['text'=>"🛠️ Sozlamalar"]],
]]);

$main_menuad = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"$tugma1"]],
[['text'=>"$tugma2"],['text'=>"$tugma3"]],
[['text'=>"$tugma5"],['text'=>"$tugma4"]],
[['text'=>"🛠️ Sozlamalar"]],
[['text'=>"🗄 Boshqaruv"]],
]]);

$asosiy_soz = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"*⃣ Birlamchi sozlamalar"]],
[['text'=>"📢 Kanallar"],['text'=>"🤖 Bot holati"]],
[['text'=>"🔑 Api sozlamalari"]],
[['text'=>"🤖 Botlar"],['text'=>"🛍️ Xizmatlar"]],
[['text'=>"🗄 Boshqaruv"]],
]]);

if($tx == "⚙️ Asosiy sozlamalar"){
if($cid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🗄 Boshqaruv paneliga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>$asosiy_soz
]);
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🖥 Asosiy menyudasiz</b>",
'parse_mode'=>"html",
]);
}}

if($text=="🔙 Orqaga" and joinchat($cid)==true){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"Menu tanlang",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📦 Nakrutka Boʻlim",'callback_data'=>"nak_menu"]],
[['text'=>"🤖 Maker Boʻlim",'callback_data'=>"mak_menu"]],
]])
]);
}


$admin1_menu = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"⚙️ Asosiy sozlamalar"]],
[['text'=>"🎛 Tugmalar"],['text'=>"💳 Hamyonlar"]],
[['text'=>"🔎 Foydalanuvchini boshqarish"]],
[['text'=>"📨 Xabarnoma"],['text'=>"📊 Statistika"]],
[['text'=>"🔙 Orqaga"]],
]]);

if($data == "nak_menu"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🗄 Nakrutka boʻlimiga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>$nak_menu,
]);
unlink("step/odam.txt");
}

if($data == "mak_menu"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🗄 Maker boʻlimiga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>$main_menu,
]);
unlink("step/odam.txt");
}

if($data == "boshqaruv" and $ccid == $admin){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🗄 Boshqaruv paneliga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("step/odam.txt");
}

$orqaga1 = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]]
]
]);
if($tx == "🗄 Boshqaruv" and $cid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🗄 Boshqaruv paneliga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu
]);
unlink("step/$cid.txt");
unlink("miqdor.txt");
unlink("fbsh.txt");
}

$orqamak = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔚 Orqaga"]]
]
]);
if($tx == "🔚 Orqaga"){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🔚 Orqaga qaytingiz</b>",
'parse_mode'=>"html",
'reply_markup'=>$main_menu
]);
unlink("step/$cid.txt");
unlink("miqdor.txt");
unlink("fbsh.txt");
}

$orqanak = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"⬅️ Orqaga"]]
]
]);
if($tx == "⬅️ Orqaga"){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🔚 Orqaga qaytingiz</b>",
'parse_mode'=>"html",
'reply_markup'=>$nak_menu
]);
unlink("step/$cid.txt");
unlink("miqdor.txt");
unlink("fbsh.txt");
}

$oddiy_xabar = file_get_contents("oddiy.txt");
if($data == "oddiy_xabar" and $ccid==$admin){
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>$lich ta foydalanuvchiga yuboriladigan xabar matnini yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("oddiy.txt","oddiy");
}
if($oddiy_xabar=="oddiy" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("oddiy.txt");
}else{
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
bot('sendmessage',[
'chat_id'=>$admin,
'text'=>"<b>$lich ta foydalanuvchiga xabar yuborish boshlandi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$lich = file_get_contents("statistika/obunachi.txt");
$lichka = explode("\n",$lich);
foreach($lichka as $lichkalar){
$usr=bot("sendMessage",[
'chat_id'=>$lichkalar,
'text'=>$text,
'parse_mode'=>'HTML'
]);
unlink("oddiy.txt");
}}}
if($usr){
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
bot("sendmessage",[
'chat_id'=>$admin,
'text'=>"<b>$lich ta foydalanuvchiga muvaffaqiyatli yuborildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
unlink("oddiy.txt");
}

$forward_xabar = file_get_contents("forward.txt");
if($data =="forward_xabar" and $ccid==$admin){
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>$lich ta foydalanuvchiga yuboriladigan xabarni forward shaklida yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("forward.txt","forward");
}
if($forward_xabar=="forward" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("forward.txt");
}else{
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
bot('sendmessage',[
'chat_id'=>$admin,
'text'=>"<b>$lich ta foydalanuvchiga xabar yuborish boshlandi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$lich = file_get_contents("statistika/obunachi.txt");
$lichka = explode("\n",$lich);
foreach($lichka as $lichkalar){
$fors=bot("forwardMessage",[
'from_chat_id'=>$cid,
'chat_id'=>$lichkalar,
'message_id'=>$mid,
]);
unlink("forward.txt");
}}}
if($fors){
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
bot("sendmessage",[
'chat_id'=>$admin,
'text'=>"<b>$lich ta foydalanuvchiga muvaffaqiyatli yuborildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
unlink("forward.txt");
}

if($tx=="📨 Xabarnoma" and $cid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📨 Yuboriladigan xabar turini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=> json_encode([
'inline_keyboard'=>[
[['text'=>"Oddiy xabar",'callback_data'=>"oddiy_xabar"]],
[['text'=>"Forward xabar",'callback_data'=>"forward_xabar"]],
]])
]);
}

if($tx == "🤖 Botlar" and $cid == $admin){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"🤖 <b>Botlarni sozlash bo'limidasiz:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📂 Kategoriyalar",'callback_data'=>"kategoriya"]],
[['text'=>"🤖 Botlarni sozlash",'callback_data'=>"BotSet"]],
]])
]);
}

if($data == "bbosh"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"🤖 <b>Botlarni sozlash bo'limidasiz:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📂 Kategoriyalar",'callback_data'=>"kategoriya"]],
[['text'=>"🤖 Botlarni sozlash",'callback_data'=>"BotSet"]],
]])
]);
}

if($data == "kategoriya"){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📂 <b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Kategoriya qo'shish",'callback_data'=>"AdKat"]],
[['text'=>"📄 Kategoriyalar ro'yxati",'callback_data'=>"listKat"]],
[['text'=>"🔙 Orqaga",'callback_data'=>"bbosh"]]
]])
]);
}

if($data == "BotSet"){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"🤖 <b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Bot qo'shish",'callback_data'=>"AdBot"]],
[['text'=>"📄 Botlar ro'yxati",'callback_data'=>"listBot"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]]
]])
]);
}

if($data == "listKat"){
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title - sozlash","callback_data"=>"setKat-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Kategoriyalar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "setKat-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📁 <b>Kategoriya nomi:</b> $kat",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🗑 O'chirish",'callback_data'=>"delKat-$kat"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"listKat"]]
]])
]);
}

if(mb_stripos($data, "delKat-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$k = str_replace("\n".$kat."","",$kategoriya);
file_put_contents("sozlamalar/bot/kategoriya.txt",$k);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>O'chirish yakunlandi!</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"kategoriya"]]
]
])
]);
deleteFolder("sozlamalar/bot/$kat");
}

if($data == "listBot"){
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title ⏩","callback_data"=>"setBot-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Kategoriyalardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "setBot-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
$more = explode("\n",$royxat);
$soni = substr_count($royxat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"⚙ $title","callback_data"=>"bset-$title-$kat"];
$keysboard2 = array_chunk($keys, 2);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($royxat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📋 <b>Botlar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"📂 Botlar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "bset-")!==false){
$ex = explode("-",$data);
$roy = $ex[1];
$kat = $ex[2];
$narx = file_get_contents("sozlamalar/bot/$kat/$roy/narx.txt");
$tavsif = file_get_contents("sozlamalar/bot/$kat/$roy/tavsif.txt");
$type = file_get_contents("sozlamalar/bot/$kat/$roy/turi.txt");
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🤖 $type</b>

<b>💬 Bot tili:</b> O'zbekcha
<b>💵 Narxi:</b> $narx $pul
<b>🗓 Kunlik to'lov:</b> 200 $pul

📋 <b>Qo'shimcha ma'lumot:</b> <i>$tavsif</i>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🗑 O'chirish",'callback_data'=>"delBot-$kat-$roy-$type"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"listBot"]]
]])
]);
}

if(mb_stripos($data, "delBot-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$roy = $ex[2];
$type = $ex[3];
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
$k = str_replace("\n".$roy."","",$royxat);
file_put_contents("sozlamalar/bot/$kat/royxat.txt",$k);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>O'chirish yakunlandi!</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"listBot"]]
]])
]);
deleteFolder("sozlamalar/bot/$kat/$roy");
unlink("sozlamalar/bot/$type.php");
}

if($data == "AdKat"){
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi kategoriya nomini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt",'AdKat');
exit();
}

if($userstep == "AdKat"){
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
file_put_contents("sozlamalar/bot/kategoriya.txt","$kategoriya\n$text");
mkdir("sozlamalar/bot/$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b>nomli kategoriya qo'shildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
}
unlink("step/$cid.txt");
}}}

if($data == "AdBot"){
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title","callback_data"=>"addb-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$AdBot = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}

if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Qaysi kategoriyaga qo'shamiz?</b>",
'parse_mode'=>'html',
'reply_markup'=>$AdBot,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "addb-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>✅ Kategoriya tanlandi</b>

📝 Bot turini yuboring: 
<i>Stikersiz yuboring!</i>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt","turi-$kat");
exit();
}

if(mb_stripos($userstep, "turi-")!==false){
$ex = explode("-",$userstep);
$kat = $ex[1];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if(isset($text)){
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
file_put_contents("sozlamalar/bot/$kat/royxat.txt","$royxat\n$text");
mkdir("sozlamalar/bot/$kat/$text");
file_put_contents("sozlamalar/bot/$kat/$text/turi.txt",$text);
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b>nomi qabul qilindi.</b>

📝 Bot uchun narx yuboring:",
'parse_mode'=>'html',
]);
file_put_contents("step/$cid.txt","narxi-$kat-$text-$text");
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>⚠️ Faqat harflardan foydalaning!</b>",
'parse_mode'=>'html',
]);
}}}

if(mb_stripos($userstep, "narxi-")!==false){
$ex = explode("-",$userstep);
$kat = $ex[1];
$roy = $ex[2];
$type = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
unlink("sozlamalar/bot/$kat/$roy");
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
$k = str_replace("\n".$roy."","",$royxat);
file_put_contents("sozlamalar/bot/$kat/royxat.txt",$k);
}else{
if(is_numeric($text)==true){
file_put_contents("sozlamalar/bot/$kat/$roy/narx.txt",$text);
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>$text </b>$pul narxi qabul qilindi

📝 Bot haqida malumot yuboring:",
'parse_mode'=>'html',
]);
file_put_contents("step/$cid.txt","tavsif-$kat-$roy-$type");
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>⚠️ Faqat raqamlardan foydalaning!</b>",
'parse_mode'=>'html',
]);
}}}

if(mb_stripos($userstep, "tavsif-")!==false){
$ex = explode("-",$userstep);
$kat = $ex[1];
$roy = $ex[2];
$type = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
unlink("sozlamalar/bot/$kat/$roy");
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
$k = str_replace("\n".$roy."","",$royxat);
file_put_contents("sozlamalar/bot/$kat/royxat.txt",$k);
}else{
if(isset($text)){
file_put_contents("sozlamalar/bot/$kat/$roy/tavsif.txt",$text);
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Qabul qilindi</b>

🗂 Bot kodini yuboring: $type.php bo'lishi kerak!",
'parse_mode'=>'html',
]);
file_put_contents("step/$cid.txt","script-$kat-$roy-$type");
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>⚠️ Faqat harflardan foydalaning!</b>",
'parse_mode'=>'html',
]);
}}}

if(mb_stripos($userstep, "script-")!==false){
$ex = explode("-",$userstep);
$kat = $ex[1];
$roy = $ex[2];
$type = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
unlink("sozlamalar/bot/$kat/$roy");
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
$k = str_replace("\n".$roy."","",$royxat);
file_put_contents("sozlamalar/bot/$kat/royxat.txt",$k);
}else{
if(isset($doc)){
$url = json_decode(file_get_contents('https://api.telegram.org/bot'.API_KEY.'/getFile?file_id='.$doc_id),true);
$path=$url['result']['file_path'];
$file = 'https://api.telegram.org/file/bot'.API_KEY.'/'.$path;
$ok = file_put_contents("botlar/$type.php",file_get_contents($file));
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>✅ Yangi bot qo'shildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
unlink("step/$cid.txt");
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Qabul qilindi</b>

🗂 Bot kodini yuboring: $type.php bo'lishi kerak!",
'parse_mode'=>'html',
]);
}}}

$taklif=file_get_contents("taklif.txt");
if($data=="taklif_narxi" and $ccid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📝 Yangi qiymatni yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("taklif.txt","taklif");
}
if($taklif == "taklif" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("taklif.txt");
}else{
file_put_contents("sozlamalar/pul/referal.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Muvaffaqiyatli o'zgartirildi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu
]);
unlink("taklif.txt");
}}

$valyuta=file_get_contents("valyuta.txt");
if($data=="valyuta_nomi" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📝 Yangi qiymatni yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("valyuta.txt","valyuta");
}
if($valyuta == "valyuta" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("valyuta.txt");
}else{
file_put_contents("sozlamalar/pul/valyuta.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Muvaffaqiyatli o'zgartirildi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu
]);
unlink("valyuta.txt");
}}

$fbsh = file_get_contents("fbsh.txt");
if($tx=="🔎 Foydalanuvchini boshqarish" and $cid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Kerakli foydalanuvchining ID raqamini yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("fbsh.txt","idraqam");
}

if($fbsh=="idraqam" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("fbsh.txt");
}else{
if(file_exists("ban/$tx.txt")){
if(file_exists("foydalanuvchi/hisob/$tx.txt")){
file_put_contents("step/odam.txt",$tx);
$asos = file_get_contents("foydalanuvchi/hisob/$tx.txt");
$tpul = file_get_contents("foydalanuvchi/hisob/$tx.1txt");
$kirit=file_get_contents("foydalanuvchi/hisob/$tx.1.txt");
$odam = file_get_contents("foydalanuvchi/referal/$tx.txt");
bot("sendMessage",[
"chat_id"=>$admin,
"text"=>"<b>✅ Foydalanuvchi topildi:</b> <a href='tg://user?id=$tx'>$tx</a>

<b>Asosiy balans:</b> $asos $pul
<b>Sarmoya balans:</b> $tpul $pul
<b>Takliflari:</b> $odam ta

<b>Kiritgan pullari:</b> $kirit $pul",
'parse_mode'=>"html",
"reply_markup"=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔕 Bandan olish",'callback_data'=>"unban"]],
[['text'=>"➕ Pul qo'shish",'callback_data'=>"val_qoshish"],['text'=>"➖ Pul ayirish",'callback_data'=>"val_ayirish"]],
[['text'=>"📊 Sarmoya qo'shish",'callback_data'=>"tolov_qoshish"],['text'=>"📊 Sarmoya ayirish",'callback_data'=>"tolov_ayirish"]],
]])
]); 
unlink("fbsh.txt");
}else{
bot('SendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Ushbu foydalanuvchi botdan foydalanmaydi!</b>

<i>Qayta yuboring:</i>",
'parse_mode'=>'html',
]);
}}else{
if(file_exists("foydalanuvchi/hisob/$tx.txt")){
file_put_contents("step/odam.txt",$tx);
$asos = file_get_contents("foydalanuvchi/hisob/$tx.txt");
$tpul = file_get_contents("foydalanuvchi/hisob/$tx.1txt");
$kirit=file_get_contents("foydalanuvchi/hisob/$tx.1.txt");
$odam = file_get_contents("foydalanuvchi/referal/$tx.txt");
bot("sendMessage",[
"chat_id"=>$admin,
"text"=>"<b>✅ Foydalanuvchi topildi:</b> <a href='tg://user?id=$tx'>$tx</a>

<b>Asosiy balans:</b> $asos $pul
<b>Sarmoya balans:</b> $tpul $pul
<b>Takliflari:</b> $odam ta

<b>Kiritgan pullari:</b> $kirit $pul",
'parse_mode'=>"html",
"reply_markup"=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔔 Banlash",'callback_data'=>"ban"]],
[['text'=>"➕ Pul qo'shish",'callback_data'=>"val_qoshish"],['text'=>"➖ Pul ayirish",'callback_data'=>"val_ayirish"]],
[['text'=>"📊 Sarmoya qo'shish",'callback_data'=>"tolov_qoshish"],['text'=>"📊 Sarmoya ayirish",'callback_data'=>"tolov_ayirish"]],
]])
]);
unlink("fbsh.txt");
}else{
bot('SendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Ushbu foydalanuvchi botdan foydalanmaydi!</b>

<i>Qayta yuboring:</i>",
'parse_mode'=>'html',
]);
}}}}

if($data=="ban"){
file_put_contents("ban/$saved.txt","ban");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<a href='tg://user?id=$saved'>$saved</a> <b>banlandi</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
bot('sendMessage',[
'chat_id'=>$saved,
'text'=>"<b>Admin tomonidan bloklandingiz!</b>",
'parse_mode'=>"html",
]);
unlink("step/odam.txt");
}

if($data=="unban"){
unlink("ban/$saved.txt");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<a href='tg://user?id=$saved'>$saved</a> <b>banlandan olindi</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
bot('sendMessage',[
'chat_id'=>$saved,
'text'=>"<b>Admin tomonidan blokdan olindingiz!</b>",
'parse_mode'=>"html",
]);
unlink("step/odam.txt");
}

$valqosh = file_get_contents("valqosh.txt");
if($data == "val_qoshish" and $ccid==$admin){
file_put_contents("valqosh.txt","valqosh");
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'parse_mode'=>"html",
'text'=>"<a href='tg://user?id=$saved'>$saved</a> <b>ning hisobiga qancha pul qo'shmoqchisiz?</b>",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
}

if($valqosh == "valqosh" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("valqosh.txt");
unlink("step/odam.txt");
}else{
bot('sendMessage',[
'chat_id'=>$saved,
'text'=>"<b>Adminlar tomonidan hisobingiz $tx $pul to'ldirildi</b>",
'parse_mode'=>"html",
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Foydalanuvchi hisobiga $tx $pul qo'shildi</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$currency=file_get_contents("foydalanuvchi/hisob/$saved.1.txt");
$get = file_get_contents("foydalanuvchi/hisob/$saved.txt");
$get += $tx;
$currency += $tx;
file_put_contents("foydalanuvchi/hisob/$saved.1.txt",$currency);
file_put_contents("foydalanuvchi/hisob/$saved.txt", $get);
unlink("valqosh.txt");
unlink("step/odam.txt");
}}

$valayir = file_get_contents("valayir.txt");
if($data == "val_ayirish" and $ccid==$admin){
file_put_contents("valayir.txt","valayir");
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'parse_mode'=>"html",
'text'=>"<a href='tg://user?id=$saved'>$saved</a> <b>ning hisobidan qancha pul ayirmoqchisiz?</b>",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
}

if($valayir == "valayir" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("valayir.txt");
unlink("step/odam.txt");
}else{
bot('sendMessage',[
'chat_id'=>$saved,
'text'=>"<b>Adminlar tomonidan hisobingizdan $tx $pul olib tashlandi</b>",
'parse_mode'=>"html",
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Foydalanuvchi hisobidan $tx $pul olib tashlandi</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$currency=file_get_contents("foydalanuvchi/hisob/$saved.1.txt");
$get = file_get_contents("foydalanuvchi/hisob/$saved.txt");
$get -= $tx;
$currency -= $tx;
file_put_contents("foydalanuvchi/hisob/$saved.1.txt",$currency);
file_put_contents("foydalanuvchi/hisob/$saved.txt", $get);
unlink("valayir.txt");
unlink("step/odam.txt");
}}

$tolqosh = file_get_contents("tvalqosh.txt");
if($data=="tolov_qoshish" and $ccid==$admin){
file_put_contents("tvalqosh.txt","tvalqosh");
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'parse_mode'=>"html",
'text'=>"<a href='tg://user?id=$saved'>$saved</a> <b>ning sarmoya hisobiga qancha pul qo'shmoqchisiz?</b>",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
}

if($tolqosh == "tvalqosh" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tvalqosh.txt");
unlink("step/odam.txt");
}else{
bot('sendMessage',[
'chat_id'=>$saved,
'text'=>"<b>Adminlar tomonidan sarmoya hisobingiz $tx $pul to'ldirildi</b>",
'parse_mode'=>"html",
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Foydalanuvchi sarmoya hisobiga $tx $pul qo'shildi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$currency=file_get_contents("foydalanuvchi/hisob/$saved.1.txt");
$currency += $tx;
file_put_contents("foydalanuvchi/hisob/$saved.1.txt",$currency);
$buyurtmab=file_get_contents("foydalanuvchi/hisob/$saved.1txt");
$buyurtmab+= $tx;
file_put_contents("foydalanuvchi/hisob/$saved.1txt", $buyurtmab);
unlink("tvalqosh.txt");
unlink("step/odam.txt");
}}

$tolayir = file_get_contents("tvalayir.txt");
if($data=="tolov_ayirish" and $ccid==$admin){
file_put_contents("tvalayir.txt","tvalayir");
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'parse_mode'=>"html",
'text'=>"<a href='tg://user?id=$saved'>$saved</a> <b>ning sarmoya hisobidan qancha pul ayirmoqchisiz?</b>",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
}

if($tolayir == "tvalayir" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tvalayir.txt");
unlink("step/odam.txt");
}else{
bot('sendMessage',[
'chat_id'=>$saved,
'text'=>"<b>Adminlar tomonidan sarmoya hisobingizdan $tx $pul olib tashlandi</b>",
'parse_mode'=>"html",
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Foydalanuvchi sarmoya hisobidan $tx $pul olib tashlandi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$currency=file_get_contents("foydalanuvchi/hisob/$saved.1.txt");
$currency -= $tx;
file_put_contents("foydalanuvchi/hisob/$saved.1.txt",$currency);
$buyurtmab=file_get_contents("foydalanuvchi/hisob/$saved.1txt");
$buyurtmab-= $tx;
file_put_contents("foydalanuvchi/hisob/$saved.1txt", $buyurtmab);
unlink("tvalayir.txt");
unlink("step/odam.txt");
}}

if($tx=="💳 Hamyonlar" and $cid==$admin){
$kategoriya = file_get_contents("sozlamalar/hamyon/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title- ni o'chirish","callback_data"=>"delete-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"➕ Yangi to'lov tizimi qo'shish",'callback_data'=>"yangi_tolov"]];
$keysboard2[] = [['text'=>"🔗 Taklif narxi",'callback_data'=>"taklif_narxi"],['text'=>"💶 Valyuta nomi",'callback_data'=>"valyuta_nomi"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>$key,
]);
}else{
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Yangi to'lov tizimi qo'shish",'callback_data'=>"yangi_tolov"]],
[['text'=>"🔗 Taklif narxi",'callback_data'=>"taklif_narxi"],['text'=>"💶 Valyuta nomi",'callback_data'=>"valyuta_nomi"]],
]])
]);
}}

if(mb_stripos($data, "delete-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$royxat = file_get_contents("sozlamalar/hamyon/kategoriya.txt");
$k = str_replace("\n".$kat."","",$royxat);
file_put_contents("sozlamalar/hamyon/kategoriya.txt",$k);
deleteFolder("sozlamalar/hamyon/$kat");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>To'lov tizimi o'chirildi!</b>",
'parse_mode'=>'html',
]);
}

if($data== "yangi_tolov"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>Yangi to'lov tizimi nomini yuboring:

Masalan:</b> Click",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt","tolov");
}

if($userstep=="tolov"){
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if(isset($text)){
$kategoriya2 = file_get_contents("sozlamalar/hamyon/kategoriya.txt");
file_put_contents("sozlamalar/hamyon/kategoriya.txt","$kategoriya2\n$text");
mkdir("sozlamalar/hamyon/$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Ushbu to'lov tizimidagi hamyoningiz raqamini yuboring:</b>",
'parse_mode'=>'html',
]);
file_put_contents("step/$cid.txt","raqam-$text");
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Yangi to'lov tizimi nomini yuboring:

Masalan:</b> Click",
'parse_mode'=>'html',
]);
}}}

if(mb_stripos($userstep, "raqam-")!==false){
$ex = explode("-",$userstep);
$kat = $ex[1];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
unlink("sozlamalar/hamyon/$kat");
}else{
if(is_numeric($text)){
file_put_contents("sozlamalar/hamyon/$kat/raqam.txt",$text);
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Yangi to'lov tizimi qo'shildi!</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
unlink("step/$cid.txt");
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Ushbu to'lov tizimidagi hamyoningiz raqamini yuboring:</b>",
'parse_mode'=>'html',
]);
}}}

if($tx=="🎛 Tugmalar" and $cid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🎛 Tugma sozlash bo'limidasiz tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🖥 Asosiy menyudagi tugmalar",'callback_data'=>"asosiy_tugma"]],
[['text'=>"💵 Pul ishlash bo'limi tugmalari",'callback_data'=>"pulishlash_tugma"]],
[['text'=>"⚠️ O'z holiga qaytarish",'callback_data'=>"reset_tugma"]],
]])
]);
}

if($data=="tugma_sozlash" and $ccid==$admin){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🎛 Tugma sozlash bo'limidasiz tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🖥 Asosiy menyudagi tugmalar",'callback_data'=>"asosiy_tugma"]],
[['text'=>"💵 Pul ishlash bo'limi tugmalari",'callback_data'=>"pulishlash_tugma"]],
[['text'=>"⚠️ O'z holiga qaytarish",'callback_data'=>"reset_tugma"]],
]])
]);
}

if($data=="asosiy_tugma" and $ccid==$admin){
bot('editMessageText',[
'chat_id'=>$admin,
'message_id'=>$cmid,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"$tugma1",'callback_data'=>"tg1"]],
[['text'=>"$tugma2",'callback_data'=>"tg2"],['text'=>"$tugma3",'callback_data'=>"tg3"]],
[['text'=>"$tugma5",'callback_data'=>"tg5"],['text'=>"$tugma4",'callback_data'=>"tg4"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"tugma_sozlash"]],
]])
]);
}

$tugma=file_get_contents("tugma.txt");
if($data=="tg1" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","tg1");
}
if($tugma == "tg1" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma1.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

$tugma=file_get_contents("tugma.txt");
if($data=="tg2" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","tg2");
}
if($tugma == "tg2" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma2.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

$tugma=file_get_contents("tugma.txt");
if($data=="tg3" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","tg3");
}
if($tugma == "tg3" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma3.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

$tugma=file_get_contents("tugma.txt");
if($data=="tg4" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","tg4");
}
if($tugma == "tg4" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma4.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

$tugma=file_get_contents("tugma.txt");
if($data=="tg5" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","tg5");
}
if($tugma == "tg5" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma5.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

if($data=="pulishlash_tugma" and $ccid==$admin){
bot('editMessageText',[
'chat_id'=>$admin,
'message_id'=>$cmid,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"$tugma7",'callback_data'=>"pultg2"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"tugma_sozlash"]],
]])
]);
}

$tugma=file_get_contents("tugma.txt");
if($data=="pultg1" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","pultg1");
}
if($tugma == "pultg1" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma6.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

$tugma=file_get_contents("tugma.txt");
if($data=="pultg2" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma uchun yangi nom yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("tugma.txt","pultg2");
}
if($tugma == "pultg2" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("tugma.txt");
}else{
file_put_contents("sozlamalar/tugma/tugma7.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Qabul qilindi!</b>

<i>Tugma nomi</i> <b>$tx</b> <i>ga o'zgartirildi</i>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
unlink("tugma.txt");
}}

if($data=="reset_tugma" and $ccid==$admin){
bot('editMessageText',[
'chat_id'=>$admin,
'message_id'=>$cmid,
'text'=>"<b>Tugma nomlari o'chirilmoqda...</b>",
'parse_mode'=>"html",
]);
sleep(2);
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Tugma nomlari o'chirilib, o'z holiga qaytarildi!</b>",
'parse_mode'=>"html",
]);
unlink("sozlamalar/tugma/tugma1.txt");
unlink("sozlamalar/tugma/tugma2.txt");
unlink("sozlamalar/tugma/tugma3.txt");
unlink("sozlamalar/tugma/tugma4.txt");
unlink("sozlamalar/tugma/tugma5.txt");
unlink("sozlamalar/tugma/tugma6.txt");
unlink("sozlamalar/tugma/tugma7.txt");
}

$admin6_menu = json_encode([
'inline_keyboard'=>[
[['text'=>"🔐 Majburiy obuna",'callback_data'=>"majburiy_obuna"]],
]]);

if($data=="kanalsoz" and $ccid==$admin){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔐 Majburiy obuna",'callback_data'=>"majburiy_obuna"]],
]])
]);
unlink("step/$ccid.txt");
}

if($tx == "📊 Statistika" and $cid == $admin){
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
$load = sys_getloadavg();
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>💡 O'rtacha yuklanish:</b> <code>$load[0]</code>

📈 <b>Aktiv botlar: $aktivbot ta</b>
📊 <b>Yaratilgan botlar: $hammabot ta</b>
👥 <b>Foydalanuvchilar: $lich ta</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔁 Yangilash",'callback_data'=>"stats"]],
[['text'=>"📊 Hisoblar",'callback_data'=>"hisob"],['text'=>"📊 Do'stlar",'callback_data'=>"dostlar"]],
]])
]);
}

if($data=="hisob" and $ccid == $admin){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
$hisoblar = hisob();
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"$hisoblar",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"stats"]],
]])
]);
}

if($data=="dostlar" and $ccid == $admin){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
$dostlar = dostlar();
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"$dostlar",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"stats"]],
]])
]);
}

if($data=="stats" and $ccid == $admin){
$lichka=file_get_contents("statistika/obunachi.txt");
$lich=substr_count($lichka,"\n");
$load = sys_getloadavg();
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>💡 O'rtacha yuklanish:</b> <code>$load[0]</code>

📈 <b>Aktiv botlar: $aktivbot ta</b>
📊 <b>Yaratilgan botlar: $hammabot ta</b>
👥 <b>Foydalanuvchilar: $lich ta</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔁 Yangilash",'callback_data'=>"stats"]],
[['text'=>"📊 Hisoblar",'callback_data'=>"hisob"],['text'=>"📊 Do'stlar",'callback_data'=>"dostlar"]],
]])
]);
}

if($tx=="📢 Kanallar" and $cid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin6_menu
]);
}

if($data=="majburiy_obuna" and $ccid==$admin){
bot('editMessageText',[
'chat_id'=>$admin,
'message_id'=>$cmid,
'text'=>"<b>Majburiy obunalarni sozlash bo'limidasiz:</b>

<i>Avval <b>asosiy kanal</b>ni ulab keyin kanal qo'shing!</i>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📋 Ro'yxatni ko'rish",'callback_data'=>"majburiy_obuna3"]],
[['text'=>"📢 Asosiy kanal",'callback_data'=>"majburiy_obuna4"],['text'=>"➕ Kanal qo'shish",'callback_data'=>"majburiy_obuna1"]],
[['text'=>"🗑 O'chirish",'callback_data'=>"majburiy_obuna2"],['text'=>"◀️ Orqaga",'callback_data'=>"kanalsoz"]],

]])
]);
unlink("step/$cid.txt");
}

$majburiy = file_get_contents("maj.txt");
if($data=="majburiy_obuna1" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📢 Kerakli kanalni manzilini yuboring:</b>

Namuna: <code>@MAKERNEWX</code>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("maj.txt","majburiy1");
}
if($majburiy == "majburiy1" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("maj.txt");
}else{
if(isset($message)){
$kanal=file_get_contents("sozlamalar/kanal/ch.txt");
if(mb_stripos($kanal,$tx)==false){
file_put_contents("sozlamalar/kanal/ch.txt", "$kanal\n$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>$tx qabul qilindi!</b>

⚠️ @$botname ni kanalingizga admin qiling!",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
}}
unlink("maj.txt");
}}

$majburiy = file_get_contents("maj.txt");
if($data=="majburiy_obuna4" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📢 Kerakli kanalni manzilini yuboring:</b>

Namuna: <code>@MAKERNEWX</code>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("maj.txt","majburiy4");
}
if($majburiy == "majburiy4" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("maj.txt");
}else{
deleteFolder("sozlamalar/kanal/ch.txt");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>$tx qabul qilindi!</b>

⚠️ @$botname ni kanalingizga admin qiling!",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
file_put_contents("sozlamalar/kanal/ch.txt","$text");
unlink("maj.txt");
}}


$majburiyoc = file_get_contents("majoch.txt");
if($data=="majburiy_obuna2" and $ccid == $admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🗑 O'chiriladigan kanal manzilini yuboring:</b>

Namuna: <code>@MAKERNEWX</code>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("majoch.txt","majoch");
}
if($majburiyoc=="majoch" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("majoch.txt");
}else{
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🗑 $tx ni o'chirish yakunlandi</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu,
]);
$kanal = file_get_contents("sozlamalar/kanal/ch.txt");
if(mb_stripos($kanal,$tx)!==false){
$ochir = str_replace("\n".$tx."","",$kanal);
file_put_contents("sozlamalar/kanal/ch.txt",$ochir);
unlink("majoch.txt");
}}}

if($data=="majburiy_obuna3" and $ccid==$admin){
if($kanallar==null){
bot('editMessageText',[
'chat_id'=>$admin,
'message_id'=>$cmid,
'text'=>"<b>Kanallar ulanmagan!</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"majburiy_obuna"]],
]])
]);
}else{
$opshi=substr_count($kanallar,"\n");
bot('editMessageText',[
'chat_id'=>$admin,
'message_id'=>$cmid,
'text'=>"<b>Ulangan kanallar ro'yxati ⤵️</b>
➖➖➖➖➖➖➖➖

<b>Asosiy kanal:</b> <i>$kanallar</i>
",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"majburiy_obuna"]],
]])
]);
}}

if($tx == "/panel"){
if($cid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🗄 Boshqaruv paneliga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>$admin1_menu
]);
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🖥 Asosiy menyudasiz</b>",
'parse_mode'=>"html",
]);
}}

if(isset($message)){
$get = file_get_contents("statistika/obunachi.txt");
if(mb_stripos($get,$fid)==false){
file_put_contents("statistika/obunachi.txt", "$get\n$fid");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>👤 Yangi aʼzo
✉️ Lichka:</b> <a href='tg://user?id=$fid'>$name</a>",
'parse_mode'=>"html"
]);
}}

if($text == "/start"){
if($cid!= $admin){
bot('sendmessage',[
'chat_id'=>$cid,
'text'=>"<b>🖥 Asosiy menyudasiz</b>",
'parse_mode'=>'html',
'reply_markup'=>$main_menu,
]);
}else{
bot('SendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🖥 Asosiy menyudasiz</b>",
'parse_mode'=>'html',
'reply_markup'=>$main_menuad,
]);
}}

if($tx=="$tugma1" and joinchat($fid)=="true"){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🤖 Botlarni boshqarish bo'limiga xush kelibsiz!</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"➕ Yangi bot ochish"]],
[['text'=>"⚙️ Botni sozlash"],['text'=>"💵 To'lov qilish"]],
[['text'=>"🗄 Buyurtmalar"],['text'=>"🔚 Orqaga"]],
]])
]);
}

if($tx=="🗄 Buyurtmalar" and joinchat($fid)=="true"){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"➕ Yangi buyurtma",url=>"tg://user?id=$admin"]],
[['text'=>"📂 Mening buyurtmam",'callback_data'=>"buyurtma_royxat"]],
]])
]);
}

if($data=="buyurtmalar" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"➕ Yangi buyurtma",url=>"tg://user?id=$admin"]],
[['text'=>"📂 Mening buyurtmam",'callback_data'=>"buyurtma_royxat"]],
]])
]);
}

if($data=="buyurtma_royxat" and joinchat($ccid)=="true"){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"⏱ <b>Yuklanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 1,
'text'=>"⏱ <b>Yuklanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🙁 Buyurtma mavjud emas!</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"◀️ Orqaga","callback_data"=>"buyurtmalar"]],
]])
]);
}

$board2=file_get_contents("foydalanuvchi/bot/$cid/bots.txt");
$more2 = explode("\n",$board2);
$soni2 = substr_count($board2,"\n");
$key2=[];
for ($for2 = 1; $for2 <= $soni2; $for2++) {
$title2=str_replace("\n","",$more2[$for2]);
$key2[]=["text"=>"💵 $title2","callback_data"=>"botpay_$title2"];
$key2board2=array_chunk($key2, 1);
$keyboard2=json_encode([
'inline_keyboard'=>$key2board2,
]);
}

if($tx=="💵 To'lov qilish" and joinchat($fid)=="true"){
$botsss = file_get_contents("foydalanuvchi/bot/$cid/bots.txt");
if($botsss){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$keyboard2,
]);
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📂 Sizda hech qanday bot yo'q</b>",
'parse_mode'=>'html',
]);
}}

if(mb_stripos($data,"orqa_")!==false){
$ex=explode("orqa_",$data)[1];
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"💵 $ex",'callback_data'=>"botpay_$ex"]],
]])
]);
}

if(mb_stripos($data,"botpay_")!==false){
$ex=explode("botpay_",$data)[1];
$turi = file_get_contents("foydalanuvchi/bot/$ccid/turi.txt");
if($turi=="ObunachiBot"){
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🗓 Necha kunlik to'lovni amalga oshirmoqchisiz?</b>

<i>1 kunlik to'lov - 200 $pul
3 kunlik to'lov - 600 $pul
7 kunlik to'lov - 1400 $pul
15 kunlik to'lov - 3000 $pul
30 kunlik to'lov - 6000 $pul</i>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"🗒 To'lov holati","callback_data"=>"holati"]],
[['text'=>"1",'callback_data'=>"dataPay=1=200=$ex"],['text'=>"3",'callback_data'=>"dataPay=3=600=$ex"],['text'=>"7",'callback_data'=>"dataPay=7=1400=$ex"],['text'=>"15",'callback_data'=>"dataPay=15=3000=$ex"],['text'=>"30",'callback_data'=>"dataPay=30=6000=$ex"]],
[["text"=>"◀️ Orqaga","callback_data"=>"botpay_$ex"]],
]])
]);
}
if($turi=="ViPObunachiBot"){
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🗓 Necha kunlik to'lovni amalga oshirmoqchisiz?</b>

<i>1 kunlik to'lov - 200 $pul
3 kunlik to'lov - 600 $pul
7 kunlik to'lov - 1400 $pul
15 kunlik to'lov - 3000 $pul
30 kunlik to'lov - 6000 $pul</i>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"🗒 To'lov holati","callback_data"=>"holati"]],
[['text'=>"1",'callback_data'=>"dataPay=1=200=$ex"],['text'=>"3",'callback_data'=>"dataPay=3=600=$ex"],['text'=>"7",'callback_data'=>"dataPay=7=1400=$ex"],['text'=>"15",'callback_data'=>"dataPay=15=3000=$ex"],['text'=>"30",'callback_data'=>"dataPay=30=6000=$ex"]],
[["text"=>"◀️ Orqaga","callback_data"=>"orqa_$ex"]],
]])
]);
}}
if(mb_stripos($data,"dataPay=")!==false){
$kun=explode("=",$data)[1];
$narx=explode("=",$data)[2];
$ex=explode("=",$data)[3];
$p=file_get_contents("foydalanuvchi/hisob/$ccid.txt");
if($p>=$narx){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>✅ Botingiz uchun $kun kunlik to'lov to'landi!</b>

<i>Hisobingizdan $narx $pul olib tashlandi</i>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"◀️ Orqaga","callback_data"=>"botpay_$ex"]],
]])
]);
file_put_contents("foydalanuvchi/hisob/$ccid.txt",$p-$narx);
date_default_timezone_set('Asia/Tashkent');
$t=date("d");
$files=json_decode(file_get_contents("foydalanuvchi/bot/$ccid/kunlik.tolov"));
$d['kun']=$files->kun+$kun;
$d['sana']=$t;
$d['puli']=$files->puli+$narx;
file_put_contents("foydalanuvchi/bot/$ccid/kunlik.tolov",json_encode($d));
}else{
bot("answerCallbackQuery",[
"callback_query_id"=>$callid,
"text"=>"😞 Kechirasiz, hisobingizda yetarli mablag' mavjud emas!",
"show_alert"=>true,
]);
}}

if($data=="holati"){
$txolat=json_decode(file_get_contents("foydalanuvchi/bot/$ccid/kunlik.tolov"));
bot("answerCallbackQuery",[
"callback_query_id"=>$callid,
"text"=>"⏳ Qolgan kunlar: ".$txolat->kun." kun",
"show_alert"=>true,
]);
}

date_default_timezone_set('Asia/Tashkent'); 
$t=date("d"); 
$glob=glob("foydalanuvchi/bot/*/turi.txt"); 
foreach($glob as $globa){ 
$ids = str_replace(["foydalanuvchi/bot/","/turi.txt"], ["",""], $globa); 
$f=file_get_contents("foydalanuvchi/bot/$ids/turi.txt"); 
$files = json_decode(file_get_contents("foydalanuvchi/bot/$ids/kunlik.tolov")); 
echo $files->kun; 
if($f=="ObunachiBot"){ 
if($files->sana!=$t){ 
$d["puli"]=$files->puli-200; 
$d["sana"]=$t; 
$d["kun"]=$files->kun-1; 
file_put_contents("foydalanuvchi/bot/$ids/kunlik.tolov",json_encode($d)); 
} 
if($files->kun==0 or $files->kun<=0){ 
bot('sendMessage',[ 
'chat_id'=>$ids, 
'text'=>"<b>Sizning botingiz uyqu rejimga o'tkazildi</b>", 
'parse_mode'=>"html", 
]); 
file_put_contents("https://api.telegram.org/bot$t/deletewebhook?url=https://".$_SERVER['SERVER_NAME']."/Nakmak/foydalanuvchi/bot/$ids/$f.php");
if($files->puli>=200){ 
date_default_timezone_set('Asia/Tashkent'); 
$t=date("d"); 
$d['sana']=$t; 
$f=$files->puli-200; 
$d['puli']=$f; 
$d['kun']=$files->kun-1; 
file_put_contents("foydalanuvchi/bot/$ids/kunlik.tolov",json_encode($d)); 
}else{ 
file_put_contents("https://api.telegram.org/bot$t/deletewebhook?url=https://".$_SERVER['SERVER_NAME']."/Nakmak/foydalanuvchi/bot/$ids/$f.php");
}}}
if($f=="ViPObunachiBot"){ 
if($files->sana!=$t){ 
$d["puli"]=$files->puli-200; 
$d["sana"]=$t; 
$d["kun"]=$files->kun-1; 
file_put_contents("foydalanuvchi/bot/$ids/kunlik.tolov",json_encode($d)); 
} 
if($files->kun==0 or $files->kun<=0){ 
bot('sendMessage',[ 
'chat_id'=>$ids, 
'text'=>"<b>Sizning botingiz uyqu rejimga o'tkazildi</b>", 
'parse_mode'=>"html", 
]); 
file_put_contents("https://api.telegram.org/bot$t/deletewebhook?url=https://".$_SERVER['SERVER_NAME']."/Nakmak/foydalanuvchi/bot/$ids/$f.php");
if($files->puli>=200){ 
date_default_timezone_set('Asia/Tashkent'); 
$t=date("d"); 
$d['sana']=$t; 
$f=$files->puli-200; 
$d['puli']=$f; 
$d['kun']=$files->kun-1; 
file_put_contents("foydalanuvchi/bot/$ids/kunlik.tolov",json_encode($d)); 
}else{ 
file_put_contents("https://api.telegram.org/bot$t/deletewebhook?url=https://".$_SERVER['SERVER_NAME']."/Nakmak/foydalanuvchi/bot/$ids/$f.php");
}}}}

$board=file_get_contents("foydalanuvchi/bot/$cid/bots.txt");
$more = explode("\n",$board);
$soni = substr_count($board,"\n");
$key=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$key[]=["text"=>"️🤖 $title","callback_data"=>"set_$title"];
$keyboard2=array_chunk($key, 2);
$keyboard=json_encode([
'inline_keyboard'=>$keyboard2,
]);
}

if($tx=="⚙️ Botni sozlash" and joinchat($fid)=="true"){
$botsss = file_get_contents("foydalanuvchi/bot/$cid/bots.txt");
if($botsss){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$keyboard,
]);
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📂 Sizda hech qanday bot yo'q</b>",
'parse_mode'=>'html',
]);
}}

$backboard=file_get_contents("foydalanuvchi/bot/$ccid/bots.txt");
$backmore = explode("\n",$backboard);
$backsoni = substr_count($backboard,"\n");
$backkey=[];
for ($backfor = 1; $backfor <= $backsoni; $backfor++) {
$title=str_replace("\n","",$backmore[$backfor]);
$backkey[]=["text"=>"️🤖 $title","callback_data"=>"set_$title"];
$backkeyboard2=array_chunk($backkey, 2);
$backkeyboard=json_encode([
'inline_keyboard'=>$backkeyboard2,
]);
}

if(mb_stripos($data,"back_")!==false){
$ex=explode("back_",$data)[1];
$botsss = file_get_contents("foydalanuvchi/bot/$ccid/bots.txt");
if($botsss){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$backkeyboard,
]);
}else{
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📂 Sizda hech qanday bot yo'q</b>",
'parse_mode'=>'html',
]);
}}

if(mb_stripos($data,"set_")!==false){
$ex=explode("set_",$data)[1];
$token=file_get_contents("foydalanuvchi/bot/$ccid/token.txt");
$turi=file_get_contents("foydalanuvchi/bot/$ccid/turi.txt");
$kunida=file_get_contents("foydalanuvchi/bot/$ccid/kunida.txt");
$soatida=file_get_contents("foydalanuvchi/bot/$ccid/soat.txt");
bot('editmessagetext',[ 
'chat_id'=>$ccid, 
'message_id'=>$cmid, 
'text'=>"<b>✅ @$ex tanlandi!</b> 
 
<b><i>🔑 Bot tokeni:</i></b> <code>$token</code> 
<b><i>🗓 Bot ochilgan vaqt:</i></b> $kunida | $soatida 
<b><i>📂 Bot turi:</i></b> <i>$turi</i> 
 
<b><i> 🔽 Quyidagi tugmalar yordamida botingizni sozlashingiz mumkin:</i></b>", 
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔑 Tokenni almashtirish",'callback_data'=>"token_$ex"]],
[['text'=>"🔄 Yangilash",'callback_data'=>"up_$ex"],['text'=>"🗑 O'chirish",'callback_data'=>"del_$ex"]],
[["text"=>"◀️ Orqaga","callback_data"=>"back_$ex"]],
]])
]);
}

if(mb_stripos($data,"kesh_")!==false){
$ex=explode("kesh_",$data)[1];
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"⏱ <b>Tozalanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 1,
'text'=>"⏱ <b>Tozalanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 2,
'text'=>"⏱ <b>Tozalanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 3,
'text'=>"⏱ <b>Tozalanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>💡 Kesh fayllar muvaffaqiyatli tozalandi</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"plus_$ex"]],
]])
]);
}

if(mb_stripos($data,"del_")!==false){
$ex=explode("del_",$data)[1];
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>⚠️ @$ex ni o'chirib yuborishga ishonchingiz komilmi?</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🗑 O'chirish",'callback_data'=>"dels_$ex"]],
[["text"=>"◀️ Orqaga","callback_data"=>"set_$ex"]],
]])
]);
}

if(mb_stripos($data,"dels_")!==false){
$ex=explode("dels_",$data)[1];
$turi = file_get_contents("foydalanuvchi/bot/$ccid/$ex/turi.txt");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🗑 @$ex ni o'chirish yakunlandi</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[["text"=>"◀️ Orqaga","callback_data"=>"back_$ex"]],
]])
]);
$aktivbot = file_get_contents("statistika/aktivbot.txt");
$aktivbot -= 1;
file_put_contents("statistika/aktivbot.txt", $aktivbot);
deleteFolder("foydalanuvchi/bot/$ccid");
$bots2 = file_get_contents("foydalanuvchi/bot/$ccid/bots.txt");
unlink("foydalanuvchi/bot/$ccid/turi.txt");
unlink("foydalanuvchi/bot/$ccid/user.json");
if(mb_stripos($bots2,$ex)!==false){
$ex1 = str_replace("\n".$ex."","",$bots2);
file_put_contents("foydalanuvchi/bot/$ccid/bots.txt",$ex1);
}}

if(mb_stripos($data,"up_")!==false){
$ex=explode("up_",$data)[1];
$turi = file_get_contents("foydalanuvchi/bot/$ccid/turi.txt");
$tokeni = file_get_contents("foydalanuvchi/bot/$ccid/token.txt");
$kod = file_get_contents("botlar/$turi.php");
$kod = str_replace("API_TOKEN", "$tokeni", $kod);
$kod = str_replace("ADMIN_ID", "$ccid", $kod);
file_put_contents("foydalanuvchi/bot/$ccid/$turi.php","$kod");
file_put_contents("foydalanuvchi/bot/$ccid/botholat.txt","activ");
$get = json_decode(file_get_contents("https://api.telegram.org/bot$tokeni/setwebhook?url=https://".$_SERVER['SERVER_NAME']."/Nakmak/foydalanuvchi/bot/$ccid/$turi.php"))->result;
if($get){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"⏱ <b>Yangilanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 1,
'text'=>"⏱ <b>Yangilanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 2,
'text'=>"⏱ <b>Yangilanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid + 3,
'text'=>"⏱ <b>Yangilanmoqda...</b>",
'parse_mode'=>'html',
]);
bot('editmessagetext',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🔄 Botingiz muvaffaqiyatli yangilandi</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➡️ Botga o'tish",'url'=>"https://t.me/$ex"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"set_$ex"]],
]])
]);
}}

if($text == "$tugma5" and joinchat($fid)=="true"){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>$tugma5-ga xush kelibsiz</b>

<i>O'z mahsulotingizni soting yoki sotib oling!</i>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Rek berish kanalda","callback_data"=>"kanalid"]],
[['text'=>"📊 Statistika","callback_data"=>"botstat"]],
[['text'=>"📋 Elon joylash",'callback_data'=>"sotish"],['text'=>"📇 Elon kuzatish",'callback_data'=>"sotib_olish"]],
]])
]);
}

$hisob = file_get_contents("foydalanuvchi/hisob/$cid.txt");
$rekkanal = file_get_contents("rek.kanal");
$reknarx = file_get_contents("rek.narx");
if($data == "kanalid" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📦 $rekkanal kanaliga reklama berish $reknarx ni tashkil etadi

💰 Sizning hisobingizda </b> $hisob $pul",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✔️ Reklama berish","callback_data"=>"kanalaydi"]],
[['text'=>"◀️ Orqaga","callback_data"=>"men"]],
]])
]);
}

$reknarx = file_get_contents("rek.narx");
if($data=="kanalaydi"){
$userstep=file_get_contents("step/$ccid.step");
	$pul = file_get_contents("foydalanuvchi/hisob/$ccid.txt"); 
	if($pul>="$reknarx"){
bot('sendmessage',[
'chat_id'=>$ccid,
'text'=>"💎 <b>Marxamat, reklamangiz matnini kiriting. Men uni kanalga joylayman!

⚠️ Faqatgina matn qabul qilinadi</b>
<b>Admin $adminuser</b>",
'parse_mode'=>"html",
'reply_markup'=>$bosh,
]);
file_put_contents("step/$ccid.txt","rektayyor");
}else{
bot('DeleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"🙁 <b>Kechirasiz, hisobingizda mablag' yetarli emas!

Agarda 500 boʻlsagina siz rek berishingiz mumkin!!!</b>

<b>Admin $adminuser</b>",
			'parse_mode'=>"html",
			'reply_markup'=>json_encode([
	'inline_keyboard'=>[
	[['text'=>"💸 Pul ishlash",'callback_data'=>"orqaga3"]],
	]]),
	]);
			}
		}
	 


$reknarx = file_get_contents("rek.narx");
$rekkanal = file_get_contents("rek.kanal");
if($userstep == "rektayyor"){
unlink("step/$cid.txt");
	if($text == "❌ Bekor qilish"){
        bot('SendMessage',[
		'chat_id'=>$ccid,
		'text'=>"🖥️ *Asosiy menyu*",
		'parse_mode'=>"markdown",
		'reply_markup'=>$menu,
		]);
		unlink("step/$cid.txt");
		}else{
			bot('SendMessage',[
			'chat_id'=>$admin,
			'text'=>"<b><a href='tg://user?id=$ccid'>$name</a>dan yangi reklama $rekkanal ga joylandi</b>",
			'parse_mode'=>"html",
			]);
			bot('SendMessage',[
		'chat_id'=>"$rekkanal",
		'text'=>"<b>#reklama

$text</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
	'inline_keyboard'=>[
	[['text'=>"💎 Tekin reklama",'url'=>"https://t.me/$botname"]],
	]]),
]);
	bot('SendMessage',[
		'chat_id'=>$ccid,
		'text'=>"💎 <b>Reklamangiz  joylandi</b>
<b>Admin $adminuser</b>",
		'parse_mode'=>"html",
		'reply_markup'=>$menu,
		]);
		unlink("step/$cid.txt");
		$balans= file_get_contents("foydalanuvchi/hisob/$cid.txt");
     $plus=$balans-"$reknarx";
  $b = file_put_contents("foydalanuvchi/hisob/$cid.txt","$plus");
		}
		}

if($data=="men" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>$tugma5-ga xush kelibsiz</b>

<i>O'z mahsulotingizni soting yoki sotib oling!</i>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📊 Statistika","callback_data"=>"botstat"]],
[['text'=>"📋 Elon joylash",'callback_data'=>"sotish"],['text'=>"📇 Elon kuzatish",'callback_data'=>"sotib_olish"]],
]])
]);
}

if($data == "botstat" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🧾 Sotuvdagi mahsulotlar soni:</b> $num ta",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🗑 Bazani tozalash","callback_data"=>"tbaza=$admin"]],
[['text'=>"◀️ Orqaga","callback_data"=>"men"]],
]])
]);
}

if(stripos($data,"tbaza=")!==false && stripos($statistika,"$callfrid")!==false){
$ex = explode("=",$data);
$odam = $ex[1];
if(stripos($admin,"$callfrid")!== false){
bot("deletemessage",[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
"chat_id"=>$odam,
"text"=>"🗑 <b>Baza tozalandi</b>",
"parse_mode"=>'html',
]);
deleteFolder("baza/");
}else{
bot('answercallbackquery',[
'callback_query_id'=>$cqid,
'text'=>"⚠️ Faqat admin tozalashi mumkin!",
'show_alert'=>true,
]);
}}

if($data == "sotish" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Mahsulotingiz haqida malumot yozing:

Namuna:</b> <code>Bot turi: Nakrutka bot
Azosi: 500 ta
Useri: @PBMemberBot
Narxi: 50.000 so'm
Obmen: Yo'q</code>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔚 Orqaga"]],
]])
]);
file_put_contents("step/$ccid.txt","bot_sotish");
}

if($userstep == "bot_sotish"){
if($cid==$admin){
if($tx=="🔚 Orqaga"){
unlink("step/$admin.txt");
}else{
$num=file_get_contents("baza/all.num");
$ok = $num + 1;
file_put_contents("baza/all.num","$ok");
file_put_contents("baza/$admin.num","$ok");
file_put_contents("baza/$ok.botext", "$tx");
file_put_contents("baza/$ok.admin",$admin);
unlink("step/$admin.txt");
bot("SendMessage",[
'chat_id'=>$admin,
'text'=>"<b>🧾 Mahsulotingiz sotuvga qo'shildi!</b>",
'parse_mode'=>'html',
'reply_markup'=>$main_menuad,
]);
unlink("step/$admin.txt");
}}else{
if($tx=="🔚 Orqaga"){
unlink("step/$cid.txt");
}else{
$num=file_get_contents("baza/all.num");
$ok = $num + 1;
file_put_contents("baza/all.num","$ok");
file_put_contents("baza/$cid.num","$ok");
file_put_contents("baza/$ok.botext", "$tx");
file_put_contents("baza/$ok.admin",$cid);
unlink("step/$cid.txt");
bot("SendMessage",[
'chat_id'=>$cid,
'text'=>"<b>🧾 Mahsulotingiz sotuvga qo'shildi!</b>",
'parse_mode'=>'html',
'reply_markup'=>$main_menu,
]);
unlink("step/$cid.txt");
}}}

if($data=="sotib_olish" and joinchat($ccid)=="true"){
$array = rand(1,$num);
$bk = $array - 1;
$ali=file_get_contents("baza/$array.botext");
if($ali){
$caption = file_get_contents("baza/$array.botext");
$ega= file_get_contents("baza/$array.admin");
bot("deletemessage",[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot("sendPhoto",[
'chat_id'=>$ccid,
'photo'=>"https://t.me/botim1chi/440",
'caption'=>"Elon raqam: $array | $soat

<b>$caption</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true, 
'inline_keyboard'=>[
[['text'=>"☎️ Murojat",url=>"tg://user?id=$ega"]],
[['text'=>"️⏪ Qaytish",'callback_data'=>"next=$bk"],['text'=>"️⏩ O'tkazish",'callback_data'=>"next=$array"]],
[['text'=>"🏠 Menyu",'callback_data'=>"men"]],
]])
]);
}else{
bot("answerCallbackQuery",[
"callback_query_id"=>$callid,
"text"=>"⚠️ Sotuvga qo'yilgan mahsulotlar topilmadi...",
"show_alert"=>true,
]);
}}

if(mb_stripos($data,"next=")!==false){
$next = explode("=",$data)[1];
$nex = $next + 1;
$bk = $next - 1;
$ali2=file_get_contents("baza/$nex.botext");
if($ali2){
$caption = file_get_contents("baza/$nex.botext");
$ega= file_get_contents("baza/$nex.admin");
bot("deletemessage",[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot("sendPhoto",[
'chat_id'=>$ccid,
'photo'=>"https://t.me/botim1chi/440",
'caption'=>"Elon raqam: $nex | $soat

<b>$caption</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true, 
'inline_keyboard'=>[
[['text'=>"☎️ Murojat",url=>"tg://user?id=$ega"]],
[['text'=>"️⏪ Qaytish",'callback_data'=>"next=$bk"],['text'=>"️⏩ O'tkazish",'callback_data'=>"next=$nex"]],
[['text'=>"🏠 Menyu",'callback_data'=>"men"]],
]])
]);
}else{
bot("answerCallbackQuery",[
"callback_query_id"=>$callid,
"text"=>"⚠️ Boshqa mahsulotlar topilmadi...",
"show_alert"=>true,
]);
}}

if($text == "➕ Yangi bot ochish" and joinchat($cid)==true){
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$key=[];
for ($for = 1; $for <= $soni; $for++) {
$title = str_replace("\n","",$more[$for]);
$key[]=["text"=>"$title","callback_data"=>"bolim-$title"];
$keyboard2 = array_chunk($key, 2);
$bolim = json_encode([
'inline_keyboard'=>$keyboard2,
]);
}
if($kategoriya == null){
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>⚠️ Kategoriyalar mavjud emas!</b>",
'parse_mode'=>'html',
]);
exit();
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"📋 <b>Quyidagi bo‘limlardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$bolim,
]);
exit();
}}

if($data == "orqaga" and joinchat($ccid)=="true"){
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$key=[];
for ($for = 1; $for <= $soni; $for++) {
$title = str_replace("\n","",$more[$for]);
$key[]=["text"=>"$title","callback_data"=>"bolim-$title"];
$keyboard2 = array_chunk($key, 2);
$bolim = json_encode([
'inline_keyboard'=>$keyboard2,
]);
}
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"📋 <b>Quyidagi bo‘limlardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>$bolim,
]);
exit();
}

if(mb_stripos($data, "bolim-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$royxat = file_get_contents("sozlamalar/bot/$kat/royxat.txt");
$kategoriya = file_get_contents("sozlamalar/bot/kategoriya.txt");
$more = explode("\n",$royxat);
$soni = substr_count($royxat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"🤖 $title","callback_data"=>"botyarat-$title-$kat"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"orqaga"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($royxat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"🤖 <b>Quyidagi botlardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"🚫 Botlar mavjud emas!",
'show_alert'=>true,
]);
}
}

if(mb_stripos($data, "botyarat-")!==false){
$bots=file_get_contents("foydalanuvchi/bot/$cid/bots.txt");
$ex = explode("-",$data);
$royxat = $ex[1];
$kategoriya = $ex[2];
$type = file_get_contents("sozlamalar/bot/$kategoriya/$royxat/turi.txt");
$narx = file_get_contents("sozlamalar/bot/$kategoriya/$royxat/narx.txt");
$tavsif = file_get_contents("sozlamalar/bot/$kategoriya/$royxat/tavsif.txt");
if($bots){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🤖 $type</b>

<b>💬 Bot tili:</b> O'zbekcha
<b>💵 Bot narxi:</b> $narx $pul
<b>🗓 Kunlik to'lov:</b> 200 $pul

📋 <b>Qo'shimcha ma'lumot:</b> <i>$tavsif</i>

🎁 Bonus sifatida 10 kunlik to'lov bepul taqdim etiladi!",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅ Yaratish",'callback_data'=>"botbor"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"bolim-$kategoriya"]],
]])
]);
}else{
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🤖 $type</b>

<b>💬 Bot tili:</b> O'zbekcha
<b>💵 Bot narxi:</b> $narx $pul
<b>🗓 Kunlik to'lov:</b> 200 $pul

📋 <b>Qo'shimcha ma'lumot:</b> <i>$tavsif</i>

🎁 Bonus sifatida 10 kunlik to'lov bepul taqdim etiladi!",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅ Yaratish",'callback_data'=>"bots-$type-$narx-$royxat-$kategoriya"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"bolim-$kategoriya"]],
]])
]);
}}

if($data =="botbor"){
bot("answerCallbackQuery",[
'callback_query_id'=>$callid,
'text'=>"⚠️ Sizda aktiv bot mavjud!",
'show_alert'=>true,
]);
}

if(mb_stripos($data, "bots-")!==false){
$ex = explode("-",$data);
$turi = $ex[1];
$narx = $ex[2];
$royxat = $ex[3];
$kategoriya = $ex[4];
$get = file_get_contents("foydalanuvchi/hisob/$ccid.txt");
if($get < $narx){
bot("answerCallbackQuery",[
'callback_query_id'=>$callid,
'text'=>"⚠️ Hisobingizda mablag' yetarli emas",
'show_alert'=>true,
]);
}else{
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🔑 Botingizni tokenini yuboring:</b>

<i>Token haqida ma'lumotga ega bo'lmasangiz qo'llanma bilan tanishib chiqing:</i>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔚 Orqaga"]],
]])
]);
file_put_contents("step/$ccid.txt","bots&token-$turi-$narx-$royxat-$kategoriya");
}}

if(mb_stripos($userstep, "bots&token-")!==false){
$ex = explode("-",$userstep);
$turi = $ex[1];
$narx = $ex[2];
$nomi = $ex[3];
$kategoriya = $ex[4];
if(mb_stripos($tx, ":")!==false){
$getid = bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>✅ Siz yuborgan bot tokeni qabul qilindi!</b>",
'parse_mode'=>'html',
])->result->message_id;
$botuser = json_decode(file_get_contents("https://api.telegram.org/bot$tx/getme"))->result->username;
$kod = file_get_contents("botlar/$turi.php");
$kod = str_replace("API_TOKEN", "$tx", $kod);
$kod = str_replace("ADMIN_ID", "$fid", $kod);

mkdir("foydalanuvchi/bot/$cid");
file_put_contents("foydalanuvchi/bot/$cid/$turi.php", $kod);

$get = json_decode(file_get_contents("https://api.telegram.org/bot$tx/setwebhook?url=https://".$_SERVER['SERVER_NAME']."/Nakmak/foydalanuvchi/bot/$cid/$turi.php"))->result;

if($get){
$botuser = json_decode(file_get_contents("https://api.telegram.org/bot$tx/getme"))->result->username;
$nomi = json_decode(file_get_contents("https://api.telegram.org/bot$tx/getme"))->result->first_name;
$id = json_decode(file_get_contents("https://api.telegram.org/bot$tx/getme"))->result->id;
mkdir("foydalanuvchi/bot/$cid");
$soat = date("H:i",strtotime("2 hour"));
$kun = date("d.m.y",strtotime("2 hour"));
file_put_contents("foydalanuvchi/bot/$cid/soat.txt","$soat");
file_put_contents("foydalanuvchi/bot/$cid/kunida.txt","$kun");
file_put_contents("foydalanuvchi/bot/$cid/token.txt","$tx");
file_put_contents("foydalanuvchi/bot/$cid/botholat.txt","activ");
file_put_contents("foydalanuvchi/bot/$cid/turi.txt","$turi");
file_put_contents("foydalanuvchi/bot/$cid/bots.txt");
if(isset($message)){
$bots=file_get_contents("foydalanuvchi/bot/$cid/bots.txt");
if(mb_stripos($bots,$botuser)==false){
file_put_contents("foydalanuvchi/bot/$cid/bots.txt", "$bots\n$botuser");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>➕ Yangi bot yaratildi!</b>

🧾 <b>Bot turi</b>: $turi
🔎 <b>Bot useri</b>: @$botuser",
'parse_mode'=>"html",
]);
sleep(0.5);
bot('deleteMessage',[
'chat_id'=>$cid,
'message_id'=>$mid,
]);
sleep(1);
bot('editMessageText',[
'chat_id'=>$cid,
'message_id'=>$getid,
'text'=>"<b>ℹ️ Botingiz tayyor. Quyidagi tugma orqali botingizga o'tishingiz mumkin.</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➡️ Botga o'tish",'url'=>"https://t.me/$botuser"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"orqagauz"]],
]])
]);
$pul = file_get_contents("foydalanuvchi/hisob/$cid.txt");
$f=$pul/200;
date_default_timezone_set('Asia/Tashkent');
$t=date("d");
$d['sana']=$t;
$d['kun']=10;
$d['puli']=2000;
file_put_contents("foydalanuvchi/bot/$cid/kunlik.tolov",json_encode($d));
$gett = file_get_contents("foydalanuvchi/hisob/$cid.txt");
$gett -= $narx;
file_put_contents("foydalanuvchi/hisob/$cid.txt", $gett);
$aktivbot = file_get_contents("statistika/aktivbot.txt");
$aktivbot += 1;
file_put_contents("statistika/aktivbot.txt", $aktivbot);
$hammabot = file_get_contents("statistika/hammabot.txt");
$hammabot += 1;
file_put_contents("statistika/hammabot.txt", $hammabot);
}}}
unlink("step/$cid.txt");
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'message_id'=>$getid,
'text'=>"<b>⛔️ Kechirasiz token qabul qilinmadi!</b>",
'parse_mode'=>"html",
]);
unlink("step/$cid.txt");
}
unlink("step/$ccid.txt");
}

if($tx=="$tugma2" and joinchat($fid)=="true"){
$odam=file_get_contents("foydalanuvchi/referal/$cid.txt");
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🔎 ID raqamingiz:</b> <code>$cid</code>

<b>💵 Asosiy balans:</b> $asosiy $pul
<b>🏦 Qo'shimcha balans:</b> $sar $pul
<b>🔗 Takliflaringiz:</b> $odam ta

<b>💳 Botga kiritgan pullaringiz:</b> $kiritgan $pul",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔁 O'tkazmalar",'callback_data'=>"puliz"]],
[['text'=>"💳 Hisobni to'ldirish",'callback_data'=>"oplata"]],
]])
]);
}

if($data == "orqaga12" and joinchat($ccid)=="true"){
$hisob = file_get_contents("foydalanuvchi/hisob/$ccid.txt");
$kiritgan = file_get_contents("foydalanuvchi/hisob/$ccid.1.txt");
$sar = file_get_contents("foydalanuvchi/hisob/$ccid.1txt");
$odam=file_get_contents("foydalanuvchi/referal/$ccid.txt");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🔎 ID raqamingiz:</b> <code>$ccid</code>

<b>💵 Asosiy balans:</b> $hisob $pul
<b>🏦 Qo'shimcha balans:</b> $sar $pul
<b>🔗 Takliflaringiz:</b> $odam ta

<b>💳 Botga kiritgan pullaringiz:</b> $kiritgan $pul",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🔁 O'tkazmalar",'callback_data'=>"puliz"]],
[['text'=>"💳 Hisobni to'ldirish",'callback_data'=>"oplata"]],
]])
]);
}



if($data == "puliz" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>Kerakli foydalanuvchi ID raqamini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔙 Orqaga"]]
]])
]);
file_put_contents("step/$ccid.txt","perevodid");
}
if($userstep == "perevodid" and $tx !== "🔙 Orqaga" and joinchat($fid)=="true"){
file_put_contents("otkazma/$fid.idraqam","$tx");
unlink("step/$cid.txt");
$getid = bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Qancha mablag'ingizni o'tkazmoqchisiz?

Hisobingiz:</b> $asosiy $pul",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔙 Orqaga"]]
]])
]);

file_put_contents("step/$cid.txt","perevodid1");
}
if($userstep == "perevodid1" and $tx !== "🔙 Orqaga" and joinchat($fid)=="true"){
file_put_contents("otkazma/$cid.pulraqam","$tx");
$raqamid = file_get_contents("otkazma/$cid.idraqam");
$raqapul = file_get_contents("otkazma/$cid.pulraqam");
$olmos1 = file_get_contents("foydalanuvchi/hisob/$raqamid.txt");
$olmos2 = file_get_contents("foydalanuvchi/hisob/$cid.txt");
$csful = $raqapul / 1 * 1;
if($olmos2>=$csful and $tx>=0){
$olmoslar1 = $olmos1 + $raqapul;
$olmoslar2 = $olmos2 - $csful;

file_put_contents("foydalanuvchi/hisob/$raqamid.txt","$olmoslar1");
file_put_contents("foydalanuvchi/hisob/$cid.txt","$olmoslar2");
bot("sendMessage",[
"chat_id"=>$raqamid,
"text"=>"<b>Hisobingizga</b> <a href='tg://user?id=$cid'>$cid</a><b> tomonidan $tx $pul o'tkazdi.</b>",
'parse_mode'=>'html',
]);
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>✅ O'tkazma muvaffaqiyatli amalga oshirildi!</b>",
'parse_mode'=>'html',
]);
unlink("step/$cid.txt");
}else{
bot("sendMessage",[
"chat_id"=>$cid,
"text"=>"<b>⚠️ Hisobingizda mablag' yetarli emas!</b>",
'parse_mode'=>'html',
]);
}}

if($data=="oplata" and joinchat($ccid)==true){
$kategoriya = file_get_contents("sozlamalar/hamyon/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$key=[];
for ($for = 1; $for <= $soni; $for++) {
$title = str_replace("\n","",$more[$for]);
$key[]=["text"=>"$title","callback_data"=>"karta-$title"];
$keyboard2 = array_chunk($key, 1);
$keyboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"orqaga12"]];
$bolim = json_encode([
'inline_keyboard'=>$keyboard2,
]);
}
if($kategoriya == null){
bot("answerCallbackQuery",[
"callback_query_id"=>$callid,
"text"=>"⚠️ To'lov tizimlari qo'shilmagan!",
"show_alert"=>true,
]);
}else{
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>💳 Quyidagi to'lov tizimlaridan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$bolim,
]);
exit();
}}

if(mb_stripos($data, "karta-")!==false){
$ex = explode("-",$data);
$kategoriya = $ex[1];
$raqam = file_get_contents("sozlamalar/hamyon/$kategoriya/raqam.txt");
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📲 To‘lov turi:</b> <u>$kategoriya</u>

💳 Karta: <code>$raqam</code>
📝 Izoh: #ID$ccid

Almashuvingiz muvaffaqiyatli bajarilishi uchun quyidagi harakatlarni amalga oshiring: 
1) Istalgan pul miqdorini tepadagi Hamyonga tashlang
2) «✅ To'lov qildim» tugmasini bosing; 
4) Qancha pul miqdoni yuborganingizni kiritin;
3) Toʻlov haqidagi suratni botga yuboring;
3) Operator tomonidan almashuv tasdiqlanishini kuting!",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅ To'lov qildim",'callback_data'=>"tolov"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"oplata"]],
]])
]);
}

if($data == "tolov" and joinchat($ccid)=="true"){
bot('DeleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>To'lov miqdorini kiriting:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔙 Orqaga"]],
]])
]);
file_put_contents("step/$ccid.txt",'oplata');
}

if($userstep == "oplata" and joinchat($ccid)=="true"){
if($tx=="🔙 Orqaga"){
unlink("step/$cid.txt");
}else{
file_put_contents("step/hisob.$cid",$text);
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>To'lovingizni chek yoki skreenshotini shu yerga yuboring:</b>",
'parse_mode'=>'html',
]);
file_put_contents("step/$cid.txt",'rasm');
}}

if($userstep == "rasm"){
if($cid==$admin){
if($tx=="🔙 Orqaga"){
unlink("step/$fid.txt");
}else{
$photo = $message->photo;
$file = $photo[count($photo)-1]->file_id;
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"*Hisobni to'ldirganingiz haqida ma'lumot asosiy adminga yuborildi. Agar to'lovni amalga oshirganingiz haqida ma'lumot mavjud bo'lsa, hisobingiz to'ldiriladi.*",
'parse_mode'=>'MarkDown',
'reply_markup'=>$main_menuad,
]);
$hisob=file_get_contents("step/hisob.$fid");
unlink("step/$fid.txt");
bot('sendPhoto',[
'chat_id'=>$admin,
'photo'=>$file,
'caption'=>"📄 <b>Foydalanuvchidan check:

👮‍♂️ Foydalanuvchi:</b> <a href='https://tg://user?id=$cid'>$name</a>
🔎 <b>ID raqami:</b> $fid
💵 <b>To'lov miqdori:</b> $hisob $pul",
'disable_web_page_preview'=>true,
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅ Hisobini to'ldirish",'callback_data'=>"on=$fid"]],
[['text'=>"❌ Bekor qilish",'callback_data'=>"off=$fid"]],
]])
]);
}}else{
if($tx=="🔙 Orqaga"){
unlink("step/$fid.txt");
}else{
$photo = $message->photo;
$file = $photo[count($photo)-1]->file_id;
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"*Hisobni to'ldirganingiz haqida ma'lumot asosiy adminga yuborildi. Agar to'lovni amalga oshirganingiz haqida ma'lumot mavjud bo'lsa, hisobingiz to'ldiriladi.*",
'parse_mode'=>'MarkDown',
'reply_markup'=>$main_menu,
]);
$hisob=file_get_contents("step/hisob.$fid");
unlink("step/$fid.txt");
bot('sendPhoto',[
'chat_id'=>$admin,
'photo'=>$file,
'caption'=>"📄 <b>Foydalanuvchidan check:

👮‍♂️ Foydalanuvchi:</b> <a href='https://tg://user?id=$cid'>$name</a>
🔎 <b>ID raqami:</b> $fid
💵 <b>To'lov miqdori:</b> $hisob $pul",
'disable_web_page_preview'=>true,
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅ Hisobini to'ldirish",'callback_data'=>"on=$fid"]],
[['text'=>"❌ Bekor qilish",'callback_data'=>"off=$fid"]],
]])
]);
}}}

if(mb_stripos($data,"on=")!==false){
$odam=explode("=",$data)[1];
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
$hisob=file_get_contents("step/hisob.$odam");
bot('SendMessage',[
'chat_id'=>$odam,
'text'=>"<b>Hisobingiz $hisob $pul ga to'ldirildi</b>",
'parse_mode'=>'html',
]);
$currency=file_get_contents("foydalanuvchi/hisob/$odam.1.txt");
$get = file_get_contents("foydalanuvchi/hisob/$odam.txt");
$get += $hisob;
$currency += $hisob;
file_put_contents("foydalanuvchi/hisob/$odam.txt",$get);
file_put_contents("foydalanuvchi/hisob/$odam.1.txt",$currency);
bot('SendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Foydalanuvchi hisobi $hisob $pul ga to'ldirildi</b>",
'parse_mode'=>'html',
]);
unlink("step/hisob.$odam");
}

if(mb_stripos($data,"off=")!==false){
$odam=explode("=",$data)[1];
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
$hisob=file_get_contents("step/hisob.$odam");
bot('SendMessage',[
'chat_id'=>$odam,
'text'=>"<b>Hisobingizni $hisob $pul ga to'ldirish bekor qilindi</b>",
'parse_mode'=>'html',
]);
bot('SendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Foydalanuvchi cheki bekor qilindi</b>",
'parse_mode'=>'html',
]);
unlink("step/hisob.$odam");
}

if($tx=="$tugma3" and joinchat($fid)=="true"){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"$tugma7",'callback_data'=>"taklifnoma"]],
]])
]);
}

if($data == "orqaga3" and joinchat($ccid)=="true"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"$tugma7",'callback_data'=>"taklifnoma"]],
]])
]);
}

if($data == "taklifnoma" and joinchat($ccid)=="true"){
$odam=file_get_contents("foydalanuvchi/referal/$ccid.txt");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>🔗 Sizning taklif havolangiz:</b>

<code>https://t.me/$botname?start=$ccid</code>

<b>1 ta taklif uchun $taklifpul so'm beriladi

Sizning takliflaringiz: $odam ta</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"👥 Do'stlarga yuborish",'url'=>"https://t.me/share/url?url=https://t.me/$botname?start=$ccid"]],
[['text'=>"🔚 Orqaga",'callback_data'=>"orqaga3"]],
]])
]);
}

if($text=="$tugma4" and joinchat($cid)==true){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📝 Murojaat matnini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔙 Orqaga"]],
]])
]);
file_put_contents("step/$cid.txt","murojat");
}

if($data=="boglanish" and joinchat($ccid)==true){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Murojaat matnini yuboring:</b>
Siz ham o'z biznesingizni boshlang bizning bot bilan @zero_builder_bot",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔙 Orqaga"]],
]])
]);
file_put_contents("step/$ccid.txt","murojat");
}

if($userstep=="murojat"){
if($text=="🔙 Orqaga"){
unlink("step/$cid.txt");
}else{
file_put_contents("step/$cid.murojat","$cid");
$murojat=file_get_contents("step/$cid.murojat");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📨 Yangi murojat keldi:</b> $murojat

<b>📑 Murojat matni:</b> $text

<b>⏰ Kelgan vaqti:</b> $soat",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"💌 Javob yozish",'callback_data'=>"yozish=$murojat"]],
]])
]);
unlink("step/$murojat.txt");
if($cid==$admin){
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>✅ Murojaatingiz yuborildi.</b>

<i>Tez orada javob qaytaramiz!</i>",
'parse_mode'=>'html',
'reply_markup'=>$main_menuad,
]);
}else{
bot('sendMessage',[
'chat_id'=>$murojat,
'text'=>"<b>✅ Murojaatingiz yuborildi.</b>

<i>Tez orada javob qaytaramiz!</i>",
'parse_mode'=>'html',
'reply_markup'=>$main_menu,
]);
}}}

if(mb_stripos($data,"yozish=")!==false){
$odam=explode("=",$data)[1];
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>Javob matnini yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🔙 Orqaga"]],
]])
]);
file_put_contents("step/$ccid.txt","javob");
file_put_contents("step/$ccid.javob","$odam");
}

if($userstep=="javob"){
if($tx=="🔙 Orqaga"){
unlink("step/$admin.step");
unlink("step/$admin.javob");
}else{
$murojat=file_get_contents("step/$cid.javob");
bot('sendMessage',[
'chat_id'=>$murojat,
'text'=>"<b>☎️ Administrator:</b>

<i>$text</i>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"Javob yozish",'callback_data'=>"boglanish"]],
]])
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Javob yuborildi</b>",
'parse_mode'=>"html",
'reply_markup'=>$main_menuad,
]);
unlink("step/$murojat.murojat");
unlink("step/$admin.step");
unlink("step/$admin.javob");
}}

/*if($tx == "📩 Reklama Xizmati" and $cid == $admin){*/
if($text=="🛠️ Sozlamalar" and joinchat($cid)==true){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Menulardan birini tanlang</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📦 Nakrutka Boʻlim",'callback_data'=>"nak_menu"]],
[['text'=>"🤖 Maker Boʻlim",'callback_data'=>"mak_menu"]],
]])
]);
}

$link_by = file_get_contents("nak/$ccid/havola.txt");
$son_by = file_get_contents("nak/$ccid/nechta.txt");

if($text == "📦 Buyurtma berish" and joinchat($cid)==true){
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$key=[];
for ($for = 1; $for <= $soni; $for++) {
$title = str_replace("\n","",$more[$for]);
$titlle = str_replace("\n","",$more[$for]);
$key[]=["text"=>"$title","callback_data"=>"nakkat-$title"];
$keyboard2 = array_chunk($key, 2);
$nakkat = json_encode([
'inline_keyboard'=>$keyboard2,
]);
}
if($kategoriya == null){
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>⚠️ Kategoriyalar mavjud emas!</b>",
'parse_mode'=>'html',
]);
exit();
}else{
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📱 Quyidagi ijtimoiy tarmoqlardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$nakkat,
]);
exit();
}}

$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
if($data == "bass" and joinchat($ccid)=="true"){
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$key=[];
for ($for = 1; $for <= $soni; $for++) {
$title = str_replace("\n","",$more[$for]);
$key[]=["text"=>"$title","callback_data"=>"nakkat-$title"];
$keyboard2 = array_chunk($key, 2);
$nakkat = json_encode([
'inline_keyboard'=>$keyboard2,
]);
}
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📱 Quyidagi ijtimoiy tarmoqlardan birini tanlang:</b>",
'parse_mode'=>"html",
'reply_markup'=>$nakkat,
]);
exit();
}

if(mb_stripos($data, "nakkat-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$xizmat = file_get_contents("sozlamalar/xizmat/$kat/xizmat.txt");
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$xizmat);
$soni = substr_count($xizmat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title","callback_data"=>"ichkinak-$title-$kat"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bass"]];
$ichkinak = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($xizmat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>⬇️ Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$ichkinak,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"📂 Xizmatlar mavjud emas!",
'show_alert'=>true,
]);
}
}

if(mb_stripos($data, "ichkinak-")!==false){
$ex = explode("-",$data);
$xiz = $ex[1];
$kat = $ex[2];
$xizmat = file_get_contents("sozlamalar/xizmatlar/$kat/$xiz.txt");
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$xizmat);
$soni = substr_count($xizmat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title","callback_data"=>"buyurtma_berish-$title-$kat"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bass"]];
$xizmatlarim = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($xizmat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>⬇️ Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$xizmatlarim,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"📂 Xizmatlar mavjud emas!",
'show_alert'=>true,
]);
}
}

if(mb_stripos($data, "buyurtma_berish-")!==false){
$ex = explode("-",$data);
$royxat = $ex[1];
$kategoriya = $ex[2];
$id = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/id.txt");
$narxi = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/narxi.txt");
$tavsif = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/tavsiya.txt");
$min = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/min.txt");
$max = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/max.txt");
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🚀 Xizmat nomi: $royxat

🆔 Xizmat ID'si: $id
💰 Narxi (1000x): $narxi $pul
📑 Malumot:</b> $tavsif

⏬ Minimal buyurtma - $min ta
⏫ Maksimal buyurtma - $max ta",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅ Buyurtma berish",'callback_data'=>"tanla-$royxat-$narxi-$min-$max-$kategoriya-$id"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"bass"]],
]])
]);
}

mkdir("nak");
mkdir("nak/$cid");
$step = file_get_contents("step/$cid.step");
$api_kalit=file_get_contents("sozlamalar/api_kalit.txt");
$api_sayt=file_get_contents("sozlamalar/api_sayt.txt");
$holat = file_get_contents("sozlamalar/holat.txt");
if(mb_stripos($data, "tanla-")!==false){
$ex = explode("-",$data);
$turi = $ex[1];
$narx = $ex[2];
$min = $ex[3];
$max = $ex[4];
$orid = $ex[6];
$ba = $ex[8];
$kategoriya = $ex[5];
 bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$ccid,
]);
bot('SendMessage',[
'chat_id'=>$ccid,
'text'=>"*📎 Kerakli havolani kiriting (https://):*",
'parse_mode'=>'markdown',
'reply_markup'=>$back
]);
    file_put_contents("step/$ccid.step","botsin-$turi-$narx-$min-$max-$kategoriya-$orid-$ba");
}

if(mb_stripos($step, "botsin-")!==false){
$ex = explode("-",$step);
$turi = $ex[1];
$narx = $ex[2];
$min = $ex[3];
$max = $ex[4];
$kategoriya = $ex[5];
$orid = $ex[6];
$ba = $ex[7];
if(isset($text)){		
file_put_contents("nak/$cid/havola.txt",$text);
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"*⬇️ Kerakli buyurtma miqdorini kiriting:*",
'parse_mode'=>'markdown',
]);
file_put_contents("step/$cid.step","vjfin-$turi-$narx-$min-$max-$orid-$ba");
exit();
}
}

if(mb_stripos($step, "vjfin-")!==false){
$ex = explode("-",$step);
$tur = $ex[1];
$narx = $ex[2];
$min = $ex[3];
$max = $ex[4];
$orid = $ex[5];
$ba = $ex[6];
if(is_numeric($text) and $text>0){
if($text>=$min and $text<=$max){
file_put_contents("nak/$cid/nechta.txt",$text);
$link_by = file_get_contents("nak/$cid/havola.txt");
$soni_by = file_get_contents("nak/$cid/nechta.txt");
$rak=$text/1000*$narx;
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>➡️ Ma'lumotlarni o'qib chiqing:

💵 Buyurtma narxi: $rak $pul
📎 Buyurtma manzili:</b> <code> $link_by </code>
🔢 Buyurtma miqdori: <code> $soni_by </code> ta

<b>⚠️ Ma'lumotlar to'g'ri bo'lsa (✅ Yuborish) tugmasiga bosing va sizning xisobingizdan $rak $pul miqdorda pul yechib olinadi va buyurtma yuboriladi buyurtmani bekor qilish imkoni bo'lmaydi.</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[       
[['text'=>"✅ Yuborish",'callback_data'=>"tasdiqnakin-$tur-$rak-$orid-$ba-$link-$text"],],
[['text'=>"❌️ Bekor qilish",'callback_data'=>"yopish"],],
]
])
]);
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"*⚠️ Buyurtma miqdorini notog’ri kiritilmoqda.
 
⏬ Minimal buyurtma - $min
 ⏫ Maksimal buyurtma - $max
 
🔄 Boshqa miqdor kiriting.*",
'parse_mode'=>'markdown',
'reply_markup'=>$black,
]);
}
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"*⚠️ Buyurtma miqdori faqat raqamdan tashkil topgan boʻlishi kerak!*",
'parse_mode'=>'markdown',
'reply_markup'=>$black,
]);
}
}

if(mb_stripos($data, "tasdiqnakin-")!==false){
$ex = explode("-",$data);
$turi = $ex[1];
$narx = $ex[2];
$orid = $ex[3];
$ba = $ex[4];
$link = $ex[5];
$son = $ex[6];
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$ccid,
]);
$pul = file_get_contents("foydalanuvchi/hisob/$ccid.txt");
if($pul>=$narx){
$link_by = file_get_contents("nak/$ccid/havola.txt");
$son_by = file_get_contents("nak/$ccid/nechta.txt");
$urll=json_decode(file_get_contents("https://$api_sayt/api/v2/?key=$api_kalit&action=add&link=$link_by&quantity=$son_by&service=$orid"),true);
$order=$urll['order'];
$error=$urll['error'];
if(isset($error)){
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"$orid $error",
'parse_mode'=>"html",
'reply_markup'=>$menu,
]);
}else{
$mm = $pul - $narx;
file_put_contents("foydalanuvchi/hisob/$ccid.txt","$mm");
bot('sendMessage',[
'chat_id'=>$ccid,
 'text'=>"✅ Buyurtma qabul qilindi!

 Buyurtma IDsi: <code>$order</code>

Yuqoridagi ID orqali buyurtmangiz haqida ma'lumot olishingiz mumkin!",
'parse_mode'=>"html",
'disable_web_page_preview'=>true,
'reply_markup'=>$main_menu,
]);
$bson=file_get_contents("foydalanuvchi/buyurtma/$ccid.txt");
$b = $bson +1;
file_put_contents("foydalanuvchi/buyurtma/$ccid.txt","b");
//
unlink("step/$ccud.step");
unlink("nak/$ccid/havola.txt");
unlink("nak/$ccid/nechta.txt");
}
}else{
bot('sendmessage',[
'chat_id'=>$ccid,
'text'=>"⚠️ Balansingizda mablag' yetarli emas!",
'reply_markup'=>$main_menu,
]);
}
unlink("step/$ccid.step");
unlink("nak/$ccid/havola.txt");
unlink("nak/$ccid/nechta.txt");
}

if($data == "yopish" and joinchat($ccid)=="true"){
unlink("step/$ccid.step");
unlink("nak/$ccid/havola.txt");
unlink("nak/$ccid/nechta.txt");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
}


mkdir("status");
mkdir("$cid");

$api_kalit=file_get_contents("sozlamalar/api_kalit.txt");
$api_sayt=file_get_contents("sozlamalar/api_sayt.txt");
$okstat=file_get_contents("status/$cid.status");
if($text=="📊 Buyurtma kuzatish" and joinchat($cid)==true){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"*🆔 Buyurtma ID sini kiriting:*",
'parse_mode'=>"MarkDown",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"⬅️ Orqaga"]]
]])
]);
mkdir("status");
file_put_contents("status/$cid.status","1");
}
if($okstat==1){
if(is_numeric($text)){
$orderstat=json_decode(file_get_contents("https://$api_sayt/api/v2?key=$api_kalit&action=status&order=$text"),true);
$miqdor=$orderstat['remains'];
$xolati=$orderstat['status'];
if($orderstat['status'] !=null or $orderstat['remains'] !=null){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"*
🆔 Buyurtma idsi: $text
🔎 Buyurtmangiz: $xolati
🔢 Qoldiq miqdori: $miqdor ta*",
'parse_mode'=>"MarkDown",
'reply_markup'=>$main_menu,
]);unlink("status/$cid.status");
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"*🤷‍♂ Mavjud emas!*" ,
'parse_mode'=>"MarkDown",
]);
unlink("status/$cid.status");
}
}
}


if($tx == "🛍️ Xizmatlar" and $cid == $admin){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"🛍️ <b>Xizmatlar sozlash bo'limidasiz:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📂 Bo'lim",'callback_data'=>"kategoriyaxiz"]],
[['text'=>"📂 Ichki bolim",'callback_data'=>"ichki"]],
[['text'=>"🛍️ Xizmatlar",'callback_data'=>"xizmat"]],
]])
]);
}

if($data == "kategoriyaxiz"){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📂 <b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Kategoriya qo'shish",'callback_data'=>"adbolim"]],
[['text'=>"🗑 Kategoriya",'callback_data'=>"delbolim"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"nakxiz"]]
]])
]);
}

if($data == "xizmat"){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📂 <b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Ichki xizmat qo'shish",'callback_data'=>"IchkiAdXiz"]],
[['text'=>"🗑️ Oʻchirish",'callback_data'=>"xizochir"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"nakxiz"]]
]])
]);
}

//Add Xizmat

if($data == "IchkiAdXiz"){
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title - sozlash","callback_data"=>"ichkisetxiz-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$keyy = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Kategoriyalar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$keyy,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "ichkisetxiz-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$xizmat = file_get_contents("sozlamalar/xizmat/$kat/xizmat.txt");
$more = explode("\n",$xizmat);
$soni = substr_count($xizmat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title - sozlash","callback_data"=>"xizmatset-$title-$kat"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$keyyy = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($xizmat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Xizmatlar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$keyyy,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Xizmatlar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "xizmatset-")!==false){
$ex = explode("-",$data);
$xiz = $ex[1];
$kat = $ex[2];
mkdir("sozlamalar/xizmatlar/$kat");
mkdir("sozlamalar/xizmatlar/$kat/$xiz");
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi xizmat nomini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt","royhatset-$xiz-$kat");
}
if(mb_stripos($userstep, "royhatset-")!==false){
$ex = explode("-",$userstep);
$xiz = $ex[1];
$roy = $ex[2];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
mkdir("sozlamalar/xizmatlar/$roy/$text");
$royhat = file_get_contents("sozlamalar/xizmatlar/$roy/$xiz.txt");
file_put_contents("sozlamalar/xizmatlar/$roy/$xiz.txt","$royhat\n$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b> qabul qilindi!

Xizmat narxini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$cid.txt","xizmatnarx-$xiz-$roy-$text");
}
}}}

if(mb_stripos($userstep, "xizmatnarx-")!==false){
$ex = explode("-",$userstep);
$xiz = $ex[1];
$roy = $ex[2];
$turi = $ex[3];
if($tx=="🗄 Boshqaruv"){
}else{
if($cid == $admin){
if(isset($text)){
file_put_contents("sozlamalar/xizmatlar/$roy/$turi/narxi.txt","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b> qabul qilindi!

ma'lumotlarni kiriting:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$cid.txt","xizmattavsiya-$xiz-$roy-$turi");
}}}}
if(mb_stripos($userstep, "xizmattavsiya-")!==false){
$ex = explode("-",$userstep);
$xiz = $ex[1];
$roy = $ex[2];
$turi = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
file_put_contents("sozlamalar/xizmatlar/$roy/$turi/tavsiya.txt","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b> qabul qilindi!

Minimal buyurtmani kiriting:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$cid.txt","min-$xiz-$roy-$turi");
}}}}
if(mb_stripos($userstep, "min-")!==false){
$ex = explode("-",$userstep);
$xiz = $ex[1];
$roy = $ex[2];
$turi = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
file_put_contents("sozlamalar/xizmatlar/$roy/$turi/min.txt","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b> qabul qilindi!

Maksimal buyurtmani kiriting:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
}
file_put_contents("step/$cid.txt","max-$xiz-$roy-$turi");
}}}
if(mb_stripos($userstep, "max-")!==false){
$ex = explode("-",$userstep);
$xiz = $ex[1];
$roy = $ex[2];
$turi = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
file_put_contents("sozlamalar/xizmatlar/$roy/$turi/max.txt","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b> qabul qilindi!

Ushbu Xizmat idsini kiriting:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$cid.txt","id-$xiz-$roy-$turi");
}}}}
if(mb_stripos($userstep, "id-")!==false){
$ex = explode("-",$userstep);
$xiz = $ex[1];
$roy = $ex[2];
$turi = $ex[3];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
file_put_contents("sozlamalar/xizmatlar/$roy/$turi/id.txt","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Xizmati qoʻshildi:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
}
unlink("step/$cid.txt");
}}}

if($data == "ichki"){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📂 <b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"➕ Xizmat qo'shish",'callback_data'=>"ichkiqosh"]],
[['text'=>"🗑️ Oʻchirish",'callback_data'=>"listXiz"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"nakxiz"]]
]])
]);
}

//Delete Ichki bolim

if($data == "listXiz"){
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title - sozlash","callback_data"=>"settxiz-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$keyy = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Kategoriyalar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$keyy,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "settxiz-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$xizmat = file_get_contents("sozlamalar/xizmat/$kat/xizmat.txt");
$more = explode("\n",$xizmat);
$soni = substr_count($xizmat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title - sozlash","callback_data"=>"xizmatsozlash-$title-$kat"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$keyyy = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($xizmat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Xizmatlar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$keyyy,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Xizmatlar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "xizmatsozlash-")!==false){
$ex = explode("-",$data);
$royxat = $ex[1];
$kategoriya = $ex[2];
$narxi = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/narxi.txt");
$tavsif = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/tavsiya.txt");
$min = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/min.txt");
$max = file_get_contents("sozlamalar/xizmatlar/$kategoriya/$royxat/max.txt");
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>🗄 Xizmat nomi:</b> $royxat",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🗑️ Oʻchirish",'callback_data'=>"delxizmat-$royhat-$kategoriya"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"Xizmatlar"]],
]])
]);
}

if(mb_stripos($data, "delxizmat-")!==false){
$ex = explode("-",$data);
$roy = $ex[1];
$kat = $ex[2];
$royxat = file_get_contents("sozlamalar/xizmat/$kat/xizmat.txt");
$k = str_replace("\n\n".$roy."","",$royxat);
file_put_contents("sozlamalar/xizmat/$kat/xizmat.txt",$k);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>O'chirish yakunlandi!</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"kategoriya"]]
]])
]);
deleteFolder("sozlamalar/xizmat/$kat/$roy");
}

if($data == "nakxiz"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"🛍️ <b>Xizmatlar sozlash bo'limidasiz:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📂 Bo'lim",'callback_data'=>"kategoriyaxiz"]],
[['text'=>"📂 Ichki bolim",'callback_data'=>"ichki"]],
[['text'=>"🛍️ Xizmatlar",'callback_data'=>"xizmat"]],
]])
]);
}

//Add Ichki bolim 

if($data == "ichkiqosh"){
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title","callback_data"=>"ichkiqosh-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$ichkiqosh = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Qaysi kategoriyaga qo'shamiz?</b>",
'parse_mode'=>'html',
'reply_markup'=>$ichkiqosh,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "ichkiqosh-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi xizmat nomini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt","ichkiqosh-$kat");
exit();
}
if(mb_stripos($userstep, "ichkiqosh-")!==false){
$ex = explode("-",$userstep);
$kat = $ex[1];
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
mkdir("sozlamalar/xizmat/$kat/$text");
file_put_contents("sozlamalar/xizmat/$kat/$text/xizmat.txt");
$xizmat = file_get_contents("sozlamalar/xizmat/$kat/xizmat.txt");
file_put_contents("sozlamalar/xizmat/$kat/xizmat.txt","$xizmat\n$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b>nomli xizmat qo'shildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
}
unlink("step/$cid.txt");
}}}

//Delete bolim
if($data == "delbolim"){
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$kategoriya);
$soni = substr_count($kategoriya,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$title=str_replace("\n","",$more[$for]);
$keys[]=["text"=>"$title - sozlash","callback_data"=>"delbolim-$title"];
$keysboard2 = array_chunk($keys, 1);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"bbosh"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($kategoriya != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>📋 Kategoriyalar ro'yxati:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"😔 Kategoriyalar mavjud emas!",
'show_alert'=>true,
]);
}}
if(mb_stripos($data, "delbolim-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"📁 <b>Kategoriya nomi:</b> $kat",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"🗑 O'chirish",'callback_data'=>"deletebolim-$kat"]],
[['text'=>"◀️ Orqaga",'callback_data'=>"listKat"]]
]])
]);
}
if(mb_stripos($data, "deletebolim-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$k = str_replace("\n".$kat."","",$kategoriya);
file_put_contents("sozlamalar/xizmat/kategoriya.txt",$k);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>O'chirish yakunlandi!</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Orqaga",'callback_data'=>"kategoriya"]]
]
])
]);
deleteFolder("sozlamalar/xizmat/$kat");
}

//Add bolim

if($data == "adbolim"){
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi kategoriya nomini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt",'adbolim');
exit();
}
if($userstep == "adbolim"){
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
$kategoriya = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
file_put_contents("sozlamalar/xizmat/kategoriya.txt","$kategoriya\n$text");
mkdir("sozlamalar/xizmat/$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"$text <b>nomli kategoriya qo'shildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
}
unlink("step/$cid.txt");
}}}

if($text){
if($holat == "❌"){
if($cid == $admin){
}else{
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"⛔️ <b>Bot vaqtinchalik o'chirilgan!</b>

<i>⚙️ Botda ta'mirlash ishlari olib borilayotgan bo'lishi mumkin!</i>",
'parse_mode'=>'html',
]);
exit();
}
}else{
}
}

if($data){
if($holat == "❌"){
if($ccid == $admin){
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$qid,
'text'=>"⛔️ Bot vaqtinchalik o'chirilgan!

⚙️ Botda ta'mirlash ishlari olib borilayotgan bo'lishi mumkin!",
'show_alert'=>true,
]);
exit();
}
}else{
}
}

if($text == "🤖 Bot holati"){
if($cid == $admin){
bot('SendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🔎 Hozirgi holat:</b> $holat",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅",'callback_data'=>"holat-✅"],['text'=>"❌",'callback_data'=>"holat-❌"]],
[['text'=>"Yopish",'callback_data'=>"boshqaruv"]]
]
])
]);
}
}

if(mb_stripos($data, "holat-")!==false){
$ex = explode("-",$data);
$xolat = $ex[1];
file_put_contents("sozlamalar/holat.txt",$xolat);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$mid2,
'text'=>"<b>🔎 Hozirgi holat:</b> $xolat",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"✅",'callback_data'=>"holat-✅"],['text'=>"❌",'callback_data'=>"holat-❌"]],
[['text'=>"Yopish",'callback_data'=>"boshqaruv"]]
]
])
]);
}

$api_kalit=file_get_contents("sozlamalar/api_kalit.txt");
$api_sayt=file_get_contents("sozlamalar/api_sayt.txt");
$holat = file_get_contents("sozlamalar/holat.txt");

if($tx == "🔑 Api sozlamalari" and $cid == $admin){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>🔑 Api sozlash bo'limidasiz:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📋 Hozirgi holati",'callback_data'=>"api_holati"]],
[['text'=>"🔑 Api kalit",'callback_data'=>"Api_kalit"],['text'=>"🔑 Api sayt",'callback_data'=>"Api_sayt"]],
[['text'=>"💵 Api hisob",'callback_data'=>"Api_hisob"]],
]])
]);
}

if($data=="api_holati"){
$api_balance = json_decode(file_get_contents("https://$api_sayt/api/v2?key=$api_kalit&action=balance"),true);
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>
🔑 Api kalit: $api_kalit

🔑 Api Sayt: $api_sayt

💵 API Balansingizda
".$api_balance['balance']." $pul </b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Ortga",'callback_data'=>"api_sozlamalari"]],
]])
]);
}

if($data=="Api_hisob" and $ccid==$admin){
$api_balance = json_decode(file_get_contents("https://$api_sayt/api/v2?key=$api_kalit&action=balance"),true);
if($api_balance){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>💵 API Balansingizda
".$api_balance['balance']." $pul </b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"◀️ Ortga",'callback_data'=>"api_sozlamalari"]],
]])
]);
}else{
bot("answerCallbackQuery",[
'callback_query_id'=>$callid,
'text'=>"⚠️ Api kalit yoki api sayt kiritilmagan!",
'show_alert'=>true,
]);
}
}

$api=file_get_contents("api.txt");
if($data=="Api_kalit" and $ccid==$admin){
bot('DeleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📝 $api_sayt dan olingan api kalitni yuboring:</b>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("api.txt","kalit");
}
if($api == "kalit" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("taklif.txt");
}else{
file_put_contents("sozlamalar/api_kalit.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Muvaffaqiyatli o'zgartirildi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$asosiy_soz
]);
unlink("api.txt");
}}

if($data=="Api_sayt" and $ccid==$admin){
bot('DeleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>📝 Api olinadigan saytni yuboring:
Namuna</b> <code>Topsmm.uz</code>",
'parse_mode'=>"html",
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("api.txt","sayt");
}
if($api == "sayt" and $cid==$admin){
if($tx=="🗄 Boshqaruv"){
unlink("taklif.txt");
}else{
file_put_contents("sozlamalar/api_sayt.txt","$tx");
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>Muvaffaqiyatli o'zgartirildi!</b>",
'parse_mode'=>"html",
'reply_markup'=>$asosiy_soz
]);
unlink("api.txt");
}}

if($data == "api_sozlamalari" and $ccid == $admin){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$admin,
'text'=>"<b>🔑 Api sozlash bo'limidasiz:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📋 Hozirgi holati",'callback_data'=>"api_holati"]],
[['text'=>"🔑 Api kalit",'callback_data'=>"Api_kalit"],['text'=>"🔑 Api sayt",'callback_data'=>"Api_sayt"]],
[['text'=>"💵 Api hisob",'callback_data'=>"Api_hisob"]],
]])
]);
}

$bolim = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
if($data == "xizochir"){
$bolim = file_get_contents("sozlamalar/xizmat/kategoriya.txt");
$more = explode("\n",$bolim);
$soni = substr_count($bolim,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$ichida = file_get_contents("sozlamalar/bot/".$more[$for]."/ichkibolim.txt");
$ta = substr_count($ichida,"\n");
$keys[]=["text"=>"$more[$for] $ta->","callback_data"=>"xizdel-".$more[$for]];
$keysboard2 = array_chunk($keys, $byson);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"xizmat"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($bolim != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"🔒 Bo'limlar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "xizdel-")!==false){
$ex = explode("-",$data);
$kat = $ex[1];
$royxat = file_get_contents("sozlamalar/bot/$kat/ichkibolim.txt");
file_put_contents("step/$ccid.bol","$kat");
$more = explode("\n",$royxat);
$soni = substr_count($royxat,"\n");
$keys=[];
for ($for = 1; $for <= $soni; $for++) {
$ichida = file_get_contents("sozlamalar/bot/$kat/".$more[$for]."/xizmatbolim.txt");
$ta = substr_count($ichida,"\n");
$keys[]=["text"=>"$more[$for] $ta->","callback_data"=>"delochir-".$more[$for]];
$keysboard2 = array_chunk($keys, $ibyson);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"xizochir"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($royxat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"<b>Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"🔒 Ichki bo'limlar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "delochir-")!==false){
$ex = explode("-",$data);
$roy = $ex[1];
$kat = file_get_contents("step/$ccid.bol");
file_put_contents("step/$ccid.ich","$roy");
$royxat = file_get_contents("sozlamalar/bot/$kat/$roy/xizmatbolim.txt");
$ids = explode("\n",$royxat);
$soni = substr_count($royxat,"\n");
foreach($ids as $id){
$key = [];
$text = "";
for ($for = 1; $for <= $soni; $for++) {
$text .= "<b>$for</b> ".$ids[$for]."\n";
$key[]=["text"=>"$for","callback_data"=>"deletexiz-".$ids[$for]];
}
$keysboard2 = array_chunk($key, $xizson);
$keysboard2[] = [['text'=>"◀️ Orqaga",'callback_data'=>"xizdel-$kat"]];
$key = json_encode([
'inline_keyboard'=>$keysboard2,
]);
}
if($royxat != null){
bot('editMessageText',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
'text'=>"🗑 <b>O'chiriladigan xizmatni tanlang:</b>

$text",
'parse_mode'=>'html',
'reply_markup'=>$key,
]);
}else{
bot('answerCallbackQuery',[
'callback_query_id'=>$callid,
'text'=>"🔒 Ichki bo'limlar mavjud emas!",
'show_alert'=>true,
]);
}}

if(mb_stripos($data, "deletexiz-")!==false){
$ex = explode("-",$data);
$xiz = $ex[1];
$roy = file_get_contents("step/$ccid.ich");
$kat = file_get_contents("step/$ccid.bol");
$royxat = file_get_contents("sozlamalar/bot/$kat/$roy/xizmatbolim.txt");
$k = str_replace("\n".$xiz."","",$royxat);
file_put_contents("sozlamalar/bot/$kat/$roy/xizmatbolim.txt",$k);
bot('deleteMessage',[
'chat_id'=>$ccid,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>$xiz - nomli xizmat o'chirildi</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
deleteFolder("sozlamalar/xizmatlar/$kat/$roy/$xiz");
}



$reknarx = file_get_contents("rek.narx");
$rekkanal = file_get_contents("rek.kanal");
$adminuser = file_get_contents("admin.user");
if($tx=="*⃣ Birlamchi sozlamalar" and $cid == $admin){
bot('sendMessage',[
'chat_id'=>$cid,
'text'=>"<b>📋 Quyidagilardan birini tanlang:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'inline_keyboard'=>[
[['text'=>"📋 Hozirgi holat",'callback_data'=>"hholat"]],
[['text'=>"🔗 Taklif narxi",'callback_data'=>"taklif_narxi"],['text'=>"💶 Valyuta nomi",'callback_data'=>"valyuta_nomi"]],
[['text'=>"👨‍💻 Admin useri",'callback_data'=>"adminuser"],['text'=>"✏️ Foiz qoʻyish",'callback_data'=>"foizqoy"]],
[['text'=>"🆕 Rek kanal",'callback_data'=>"rek_kanal"],['text'=>"🆓 Rek narx",'callback_data'=>"rek_narx"]],
]])
]);
}

if($data == "rek_narx"){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi reklama narxini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt",'rek_narx');
exit();
}

//Tarqatgan kot mehnatimni qadrlela @khorn_ff & @Reliabledev
//Tarqatgan kot mehnatimni qadrlela @khorn_ff & @Reliabledev

if($userstep == "rek_narx"){
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
$reknarx = file_get_contents("rek.narx");
file_put_contents("rek.narx","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Qabul qilidim</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
}
unlink("step/$cid.txt");
}}}

if($data == "rek_kanal"){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi Reklama kanal userini yuboring:
Namuna</b> <code>@Reliabledev</code>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt",'rek_kanal');
exit();
}

//Tarqatgan kot mehnatimni qadrlela @khorn_ff & @Reliabledev
//Tarqatgan kot mehnatimni qadrlela @khorn_ff & @Reliabledev

if($userstep == "rek_kanal"){
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
$rekkanal = file_get_contents("rek.kanal");
file_put_contents("rek.kanal","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Qabul qilidim</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
}
unlink("step/$cid.txt");
}}}


if($data == "hholat"){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 

🔗 Taklif narxi - $taklifpul
💶 Valyuta nomi - $pul

👨‍💻 Admin useri - $adminuser

🆓 Reklama kanali - $rekkanal
🆕 Reklama narxi - $reknarx</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"],['text'=>"◀️ Orqaga"]],
]])
]);
exit();
}

if($data == "adminuser"){
bot('deleteMessage',[
'chat_id'=>$admin,
'message_id'=>$cmid,
]);
bot('sendMessage',[
'chat_id'=>$ccid,
'text'=>"<b>📝 Yangi admin userini yuboring:</b>",
'parse_mode'=>'html',
'reply_markup'=>json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"🗄 Boshqaruv"]],
]])
]);
file_put_contents("step/$ccid.txt",'adminuser');
exit();
}

//Tarqatgan kot mehnatimni qadrlela @khorn_ff & @Reliabledev
//Tarqatgan kot mehnatimni qadrlela @khorn_ff & @Reliabledev

if($userstep == "adminuser"){
if($tx=="🗄 Boshqaruv"){
unlink("step/$cid.txt");
}else{
if($cid == $admin){
if(isset($text)){
$adminuser = file_get_contents("admin.user");
file_put_contents("admin.user","$text");
bot('SendMessage',[
'chat_id'=>$cid,
'text'=>"<b>Qabul qilidim</b>",
'parse_mode'=>'html',
'reply_markup'=>$admin1_menu,
]);
}
unlink("step/$cid.txt");
}}}


?>
