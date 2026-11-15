$ErrorActionPreference = "Stop"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $inPath = (Resolve-Path "AI_Interview_Analyzer_ML_Project_Report.docx").Path
    $outPath = [System.IO.Path]::Combine((Get-Location).Path, "AI_Interview_Analyzer_ML_Project_Report.pdf")
    Write-Host "Opening DOCX: $inPath"
    $doc = $word.Documents.Open($inPath)
    Write-Host "Exporting PDF: $outPath"
    $doc.SaveAs([ref]$outPath, [ref]17)
    $doc.Close()
    Write-Host "Successfully compiled AI_Interview_Analyzer_ML_Project_Report.pdf!"
}
finally {
    $word.Quit()
}
