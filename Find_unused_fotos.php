#!/usr/bin/php -q
<?php
// Скрипт поиска неиспользуемых файлов в Bitrix (только список)

// Настройки
$DOCUMENT_ROOT = '/home/s/sunday84/sunday/public_html'; // Путь к корню сайта
$UPLOAD_DIR = $DOCUMENT_ROOT.'/upload/iblock/';
$OUTPUT_FILE = $DOCUMENT_ROOT.'/bitrix/catalog_export/unused_files.txt'; // Куда сохранить список

// Подключаем ядро
$_SERVER['DOCUMENT_ROOT'] = '/home/s/sunday84/sunday/public_html';
require($_SERVER['DOCUMENT_ROOT'].'/bitrix/modules/main/include/prolog_before.php');

// Проверяем подключение модулей
if (!CModule::IncludeModule('iblock') || !CModule::IncludeModule('main')) {
    die("Не удалось подключить модули\n");
}

// Сканируем все файлы в папке /upload/iblock/
function scanUploadDir($dir) {
    $files = [];
    $rii = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir));

    foreach ($rii as $file) {
        if ($file->isDir()) continue;
        $files[] = str_replace('\\', '/', $file->getPathname());
    }

    return $files;
}

echo "Сканируем папку upload/iblock/...\n";
$allFiles = scanUploadDir($UPLOAD_DIR);

// Загружаем все FILE_ID из базы
echo "Получаем список используемых файлов...\n";
$usedFiles = [];
$res = \Bitrix\Main\FileTable::getList([
    'select' => ['ID', 'SUBDIR', 'FILE_NAME']
]);

while ($file = $res->fetch()) {
    $path = $DOCUMENT_ROOT.'/upload/'.$file['SUBDIR'].'/'.$file['FILE_NAME'];
    $path = str_replace('\\', '/', $path);
    $usedFiles[$path] = true;
}

// Сравниваем
echo "Ищем неиспользуемые файлы...\n";
$unused = [];
foreach ($allFiles as $filePath) {
    if (!isset($usedFiles[$filePath])) {
        $unused[] = $filePath;
    }
}

// Сохраняем в файл
echo "Записываем список в файл...\n";
file_put_contents($OUTPUT_FILE, implode("\n", $unused));

echo "Готово! Найдено ".count($unused)." неиспользуемых файлов.\n";
echo "Список сохранен в: $OUTPUT_FILE\n";
?>