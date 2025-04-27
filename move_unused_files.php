#!/usr/local/bin/php7.2
<?php
// Устанавливаем правильные пути
$_SERVER['DOCUMENT_ROOT'] = '/home/s/sunday84/sunday/public_html';
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Путь к файлу со списком ненужных файлов
$listFile = __DIR__ . '/unused_files.txt';
// Папка, куда будем переносить неиспользуемые файлы
$backupFolder = $_SERVER['DOCUMENT_ROOT'] . '/bitrix/tmp_unused_files';
// Путь к файлу логов
$logFile = __DIR__ . '/move_unused_photos.log';

// Ограничение на количество переносов за запуск
$limit = 100;

// Проверка наличия списка файлов
if (!file_exists($listFile)) {
    die("Файл со списком не найден: $listFile\n");
}

// Получаем список файлов
$files = file($listFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

if (!$files) {
    die("Список файлов пуст.\n");
}

// Создаём папку для бэкапа, если её нет
if (!file_exists($backupFolder)) {
    mkdir($backupFolder, 0755, true);
}

$moved = 0;

foreach ($files as $filePath) {
    $filePath = trim($filePath);
    if (!$filePath) {
        continue;
    }

    // Обрезаем DOCUMENT_ROOT из пути
    $relativePath = str_replace($_SERVER['DOCUMENT_ROOT'] . '/', '', $filePath);

    $fullPath = $filePath;
    $newPath = $backupFolder . '/' . $relativePath;

    // Создаем вложенные папки внутри backup
    $targetDir = dirname($newPath);
    if (!file_exists($targetDir)) {
        mkdir($targetDir, 0755, true);
    }

    if (file_exists($fullPath)) {
        if (rename($fullPath, $newPath)) {
            file_put_contents($logFile, date('Y-m-d H:i:s') . " Перемещено: $relativePath\n", FILE_APPEND);
            $moved++;
        } else {
            file_put_contents($logFile, date('Y-m-d H:i:s') . " Ошибка перемещения: $relativePath\n", FILE_APPEND);
        }
    } else {
        file_put_contents($logFile, date('Y-m-d H:i:s') . " Файл не найден: $relativePath\n", FILE_APPEND);
    }

    if ($moved >= $limit) {
        echo "Достигнут лимит в $limit переносов за один запуск.\n";
        break;
    }
}

echo "Перенос завершен. Перемещено файлов: $moved\n";
?>