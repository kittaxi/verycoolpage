<?php
// Define the directory where files are stored
$directory = __DIR__;

// Define the file matching pattern
$pattern = '/version_distribution_\d{8}_\d{6}\.png$/';

// Get all files in the directory
$files = scandir($directory);

// Filter and sort files matching the pattern
$matchingFiles = array_filter($files, function ($file) use ($pattern) {
    return preg_match($pattern, $file);
});
usort($matchingFiles, function ($a, $b) {
    return strcmp($b, $a); // Sort descending by filename
});

// Return the latest file
if (!empty($matchingFiles)) {
    echo $matchingFiles[0];
} else {
    http_response_code(404);
    echo "No files found!";
}
?>
