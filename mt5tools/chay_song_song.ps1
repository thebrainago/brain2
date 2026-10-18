# Chay backtest v24 song song 4 terminal (mac dinh + 3 slot portable C:\MT5slots\s1..s3, co che muon tu the-brain/dung_slot_mt5.ps1).
# Ini cho slot portable dat o C:\MT5slots\ini (duong dan khong dau cach). MO PHONG / backtest, khong phai tien that.
param([string]$Syms="EURUSD#,GBPUSD#", [int]$Model=1, [int]$NSlot=4)
$R='C:\Users\DUNG\brain2\mt5run'; $OUT="$R\rep"; New-Item -ItemType Directory -Force $OUT,'C:\MT5slots\ini' | Out-Null
$D="$env:APPDATA\MetaQuotes\Terminal\BB16F565FAAA6B23A20C26C49416FF05"
$slots=@(@{exe='C:\Program Files\XM Global MT5\terminal64.exe';dat=$D;port=$false})
1..3 | % { $slots += @{exe="C:\MT5slots\s$_\terminal64.exe";dat="C:\MT5slots\s$_";port=$true} }
foreach($s in $slots){ New-Item -ItemType Directory -Force "$($s.dat)\MQL5\Experts\BRAIN","$($s.dat)\MQL5\Profiles\Tester" | Out-Null
  Copy-Item "$D\MQL5\Experts\BRAIN\*.ex5" "$($s.dat)\MQL5\Experts\BRAIN\" -Force
  Copy-Item "$D\MQL5\Profiles\Tester\BRAIN_V24_*.set" "$($s.dat)\MQL5\Profiles\Tester\" -Force }
$Q=New-Object System.Collections.Queue
foreach($ea in 'RSI','MRZ'){ foreach($sy in $Syms.Split(',')){ foreach($p in @('2004|2004.01.01|2015.12.31','2016|2016.01.01|2026.10.01')){ $Q.Enqueue("$ea|$sy|$p") }}}
$busy=@{}; "START $(Get-Date) n=$($Q.Count)" | Add-Content "$R\run2.log"
while($Q.Count -gt 0 -or $busy.Count -gt 0){
  foreach($i in 0..($NSlot-1)){
    if($busy.ContainsKey($i)){ $b=$busy[$i]; if(-not $b.pr.HasExited){continue}
      $s=$slots[$i]; $f=Get-ChildItem $s.dat -Filter "$($b.name).htm*" -EA SilentlyContinue | select -First 1
      if($f){ Copy-Item $f.FullName "$OUT\" -Force; Remove-Item $f.FullName }
      $lg=Get-ChildItem "$($s.dat)\Tester\logs","$($s.dat)\logs" -Filter *.log -EA SilentlyContinue | sort LastWriteTime | select -Last 1
      "$($b.name) slot$i $([int]((Get-Date)-$b.t0).TotalSeconds)s htm=$([bool]$f)" | Add-Content "$R\run2.log"; $busy.Remove($i) }
    if($Q.Count -eq 0){continue}
    $j=$Q.Dequeue().Split('|'); $ea,$sy,$tag,$fr,$to=$j; $safe=$sy -replace '[^A-Za-z0-9]','_'
    $name="v24_${ea}_${safe}_$tag"; if(Test-Path "$OUT\$name.htm"){continue}
    $ini="C:\MT5slots\ini\$name.ini"
    @"
[Tester]
Expert=BRAIN\BRAIN_V24_${ea}_Trail_D1.ex5
ExpertParameters=BRAIN_V24_${ea}_Trail_D1.set
Symbol=$sy
Period=D1
Model=$Model
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
    $s=$slots[$i]; $a=@("/config:$ini"); if($s.port){$a=@('/portable')+$a}
    $pr=Start-Process $s.exe -ArgumentList $a -PassThru; $busy[$i]=@{pr=$pr;name=$name;t0=Get-Date}
  }
  Start-Sleep 5
}
"ALL DONE $(Get-Date)" | Add-Content "$R\run2.log"
