param([string]$Jobs,[string]$Slot='D:\mt5_tester\p1')
$R='D:\mt5_tester'; $OUT="$R\rep"; New-Item -ItemType Directory -Force $OUT,"$R\ini" | Out-Null
$slots=@($Slot)
foreach($p in $slots){ foreach($g in 0,2){ (Get-Content "$p\MQL5\Profiles\Tester\BRAIN_V24_MRZ_Trail_D1.set") -replace '^InpGioVao=.*',"InpGioVao=$g" | Set-Content "$p\MQL5\Profiles\Tester\MRZ_g$g.set" -Encoding ASCII } }
$Q=New-Object System.Collections.Queue; $Jobs.Split(';') | % { $Q.Enqueue($_) }
$busy=@{}; $deadStart=(Get-Date).Date.AddHours(22).AddMinutes(10); $deadKill=(Get-Date).Date.AddHours(22).AddMinutes(35)
"START $(Get-Date) n=$($Q.Count)" | Add-Content "$R\run.log"
while($Q.Count -gt 0 -or $busy.Count -gt 0){
  Get-Process terminal64,metatester64 -EA SilentlyContinue | ? { $_.Path -like 'D:\mt5_tester*' -and $_.PriorityClass -ne 'Idle' } | % { try{$_.PriorityClass='Idle'}catch{} }
  if((Get-Date) -gt $deadKill){ "DEADLINE kill $(Get-Date)" | Add-Content "$R\run.log"; Get-Process terminal64,metatester64 -EA SilentlyContinue | ? { $_.Path -like 'D:\mt5_tester*' } | Stop-Process -Force; break }
  foreach($i in 0..0){
    $p=$slots[$i]
    if($busy.ContainsKey($i)){ $b=$busy[$i]; if(-not $b.pr.HasExited){continue}
      $f=Get-ChildItem $p -Filter "$($b.name).htm*" -EA SilentlyContinue | select -First 1
      if($f){ Move-Item $f.FullName "$OUT\" -Force }
      "$($b.name) $(Split-Path $p -Leaf) $([int]((Get-Date)-$b.t0).TotalSeconds)s htm=$([bool]$f) $(Get-Date -f HH:mm)" | Add-Content "$R\run.log"; $busy.Remove($i); if(-not $f -and ((Get-Date)-$b.t0).TotalSeconds -lt 90){ "FAIL-FAST stop queue" | Add-Content "$R\run.log"; $Q.Clear() } }
    if($Q.Count -eq 0 -or (Get-Date) -gt $deadStart){ if($Q.Count){ "SKIP (deadline) $($Q.ToArray() -join ';')" | Add-Content "$R\run.log"; $Q.Clear() }; continue }
    $sy,$g,$fr,$to,$tag=$Q.Dequeue().Split('|'); $safe=$sy -replace '[^A-Za-z0-9]','_'
    $name="v27_MRZ_${safe}_g${g}_$tag"
    $ini="$R\ini\$name.ini"
@"
[Tester]
Expert=BRAIN\BRAIN_V24_MRZ_Trail_D1.ex5
ExpertParameters=MRZ_g$g.set
Symbol=$sy
Period=D1
Model=4
ExecutionMode=0
Optimization=0
FromDate=$fr
ToDate=$to
ForwardMode=0
Deposit=10000
Currency=USD
Leverage=1:30
Report=$name
ReplaceReport=1
ShutdownTerminal=1
Visual=0
"@ | Set-Content $ini -Encoding ASCII
    $pr=Start-Process "$p\terminal64.exe" -ArgumentList '/portable',"/config:$ini" -PassThru
    Start-Sleep 2; try{$pr.PriorityClass='Idle'}catch{}
    $busy[$i]=@{pr=$pr;name=$name;t0=Get-Date}; "LAUNCH $name $(Split-Path $p -Leaf) $(Get-Date -f HH:mm)" | Add-Content "$R\run.log"
  }
  Start-Sleep 10
}
"ALL DONE $(Get-Date)" | Add-Content "$R\run.log"


