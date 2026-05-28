# ── Row 로잉앱 → GitHub Pages 배포 스크립트 ──
# 사용법: Windows Terminal(PowerShell)에서 이 파일이 있는 폴더로 이동 후 실행
#   cd "C:\Users\이진욱\OneDrive\바탕 화면\Row"
#   powershell -ExecutionPolicy Bypass -File .\deploy.ps1
#
# 중간에 브라우저 로그인(gh auth login) 1회만 직접 해주시면 나머지는 자동입니다.

$ErrorActionPreference = "Stop"
$RepoName = "Row"   # 원하면 저장소 이름 변경

# 1) gh CLI 설치 확인 (없으면 설치)
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI 설치 중..." -ForegroundColor Cyan
    winget install --id GitHub.cli --silent --accept-source-agreements --accept-package-agreements
    # 현재 세션 PATH 갱신
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "gh 가 PATH에 없습니다. 새 터미널을 열고 다시 실행해주세요." -ForegroundColor Red
    exit 1
}

# 2) GitHub 로그인 (이미 로그인돼 있으면 건너뜀)
gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nGitHub 로그인을 진행합니다. 안내에 따라 브라우저에서 로그인하세요." -ForegroundColor Cyan
    Write-Host "  (Account: GitHub.com / Protocol: HTTPS / Authenticate: Login with a web browser 권장)" -ForegroundColor DarkGray
    gh auth login
}

# 3) 저장소 생성 + 푸시 (이미 있으면 그냥 푸시)
$exists = $false
try { gh repo view $RepoName 2>$null; if ($LASTEXITCODE -eq 0) { $exists = $true } } catch {}

if (-not $exists) {
    Write-Host "`n공개 저장소 '$RepoName' 생성 + 업로드..." -ForegroundColor Cyan
    gh repo create $RepoName --public --source=. --remote=origin --push
} else {
    Write-Host "`n기존 저장소에 푸시..." -ForegroundColor Cyan
    git push -u origin master 2>$null
    if ($LASTEXITCODE -ne 0) { git push -u origin main }
}

# 4) GitHub Pages 활성화 (master 브랜치 root)
$user = gh api user --jq ".login"
Write-Host "`nGitHub Pages 활성화 중..." -ForegroundColor Cyan
$branch = (git rev-parse --abbrev-ref HEAD).Trim()
try {
    gh api -X POST "repos/$user/$RepoName/pages" -f "source[branch]=$branch" -f "source[path]=/" 2>$null
} catch {
    Write-Host "(이미 활성화돼 있거나 잠시 후 자동 활성화됩니다)" -ForegroundColor DarkGray
}

# 5) 결과 URL 출력
$pagesUrl = "https://$user.github.io/$RepoName/index.html"
Write-Host "`n========================================" -ForegroundColor Green
Write-Host " 배포 완료!" -ForegroundColor Green
Write-Host " 모바일에서 접속: $pagesUrl" -ForegroundColor Yellow
Write-Host " (Pages 빌드에 1~2분 걸릴 수 있습니다)" -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n이후 코드 수정 시 갱신 방법:" -ForegroundColor Cyan
Write-Host '  git add -A; git commit -m "update"; git push'
