set -u
D=/tmp/c211; mkdir -p $D
export PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:$PATH
W=prl1pydpjh2qzrs3sgtwpwnxntrymc2q22t3z2pg9fjx6g69gevy7twcs830sql
NOCKSUF=9becsPFXhMLCNAxb6TsMN492sS2Ev7ToLFR4zsc5K4NxRthTyh2kPcb
WK=__WK__
EPS="pool.pearlhash.xyz:9000 hk.pearlhash.net:9000 global.pearlhash.net:9000 global2.pearlhash.net:9000"
ts(){ date -u +%FT%TZ; }
if ! command -v curl >/dev/null 2>&1; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq >/dev/null 2>&1
  apt-get install -y -qq curl ca-certificates wget >/dev/null 2>&1
fi
echo "C211_I121377_START ts=$(ts) host=$(hostname) worker=$WK"
if ! nvidia-smi -L; then echo "C211_I121377_NO_GPU"; exit 3; fi
UUID=$(nvidia-smi --query-gpu=uuid --format=csv,noheader 2>/dev/null | head -1)
NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1)
echo "C211_I121377_DEVICE ts=$(ts) uuid=$UUID name=$NAME driver=$DRV worker=$WK"
ok=0
for u in https://github.com/andru-kun/wildrig-multi/releases/download/0.52.3/wildrig-multi-linux-0.52.3.tar.gz http://169.58.247.186:8791/wildrig-multi-linux-0.52.3.tar.gz; do
  if curl -fsSL --max-time 300 -o $D/wr.tgz "$u"; then ok=1; break; fi
  echo "C211_I121377_WR_DL_RETRY url=$u"
done
if [ "$ok" != "1" ]; then echo "C211_I121377_WR_DL_FAIL"; exit 4; fi
S=$(sha256sum $D/wr.tgz | awk '{print $1}')
echo "C211_I121377_WR_TGZ_SHA $S"
if [ "$S" != "7308c95f7c8c4c0d82aade61bb4ab3366decae2b9d04ac47b8c1dc6d1bdd2c44" ]; then echo "C211_I121377_WR_TGZ_BAD"; exit 5; fi
tar -xzf $D/wr.tgz -C $D || { echo "C211_I121377_WR_UNTAR_FAIL"; exit 5; }
chmod +x $D/wildrig-multi
B=$(sha256sum $D/wildrig-multi | awk '{print $1}')
if [ "$B" != "002cd29c6b890a4159b5933260e7db57d8808e540804466b3b7b80814083011b" ]; then echo "C211_I121377_WR_BIN_BAD"; exit 6; fi
echo "C211_I121377_WR_READY bin=$B"
MODE=ph; EP=""; ACC=0; REJ=0; EPI=0; HB=0; PHSTART=$(date +%s)
start_ph(){
  n=0; for e in $EPS; do n=$((n+1)); done
  pick=$(( EPI % n + 1 )); k=0
  for e in $EPS; do k=$((k+1)); if [ "$k" -eq "$pick" ]; then EP=$e; fi; done
  echo "C211_I121377_PH_START ts=$(ts) ep=$EP worker=$WK"
  ( setsid $D/wildrig-multi --algo pearlhash --url $EP --user $W --worker $WK -d 0 --print-time 60 >> $D/wr.log 2>&1 < /dev/null & )
}
install_srb(){
  ok2=0
  for u in https://github.com/doktor83/SRBMiner-Multi/releases/download/3.8.8/SRBMiner-Multi-3-8-8-Linux.tar.gz; do
    if curl -fsSL --max-time 300 -o $D/srb.tgz "$u"; then ok2=1; break; fi
  done
  if [ "$ok2" != "1" ]; then echo "C211_I121377_SRB_DL_FAIL"; return 1; fi
  S2=$(sha256sum $D/srb.tgz | awk '{print $1}')
  if [ "$S2" != "c203e79e9dc467ec5daaa1e1771e08561a70d2c9dcc397364b8ae7ae558e50d8" ]; then echo "C211_I121377_SRB_TGZ_BAD $S2"; return 1; fi
  tar -xzf $D/srb.tgz -C $D || { echo "C211_I121377_SRB_UNTAR_FAIL"; return 1; }
  X=$(find $D -maxdepth 2 -type f -name 'SRBMiner-MULTI' | head -1)
  if [ -z "$X" ]; then echo "C211_I121377_SRB_MISSING"; return 1; fi
  cp -f "$X" $D/srbminer; chmod +x $D/srbminer
  B2=$(sha256sum $D/srbminer | awk '{print $1}')
  if [ "$B2" != "b4ddc14a9a770c977b4fdc4a1e39e67e888a50e096e519a93e399eea4a826aeb" ]; then echo "C211_I121377_SRB_BIN_BAD $B2"; return 1; fi
  echo "C211_I121377_SRB_READY bin=$B2"; return 0
}
start_srb(){
  echo "C211_I121377_SRB_START ts=$(ts) pool=103.199.106.122:3362 worker=$WK"
  ( setsid $D/srbminer --disable-cpu --algorithm pearlhash --pool 103.199.106.122:3362 --wallet "$W+$NOCKSUF" --worker $WK --password x --gpu-id 0 >> $D/srb.log 2>&1 < /dev/null & )
}
hb(){
  echo "C211_I121377_HB ts=$(ts) worker=$WK mode=$MODE acc=$ACC rej=$REJ ep=$EP dev=$(nvidia-smi --query-gpu=uuid,utilization.gpu --format=csv,noheader 2>/dev/null | head -1 | tr -d '\r') last=$(grep -E 'accepted' $D/wr.log 2>/dev/null | tail -1 | tr -d '\r')"
}
start_ph
while true; do
  sleep 30
  ACC=$(grep -cE 'accepted \(' $D/wr.log 2>/dev/null || true); ACC=${ACC:-0}
  REJ=$(grep -cE 'rejected \(' $D/wr.log 2>/dev/null || true); REJ=${REJ:-0}
  case "$ACC" in ''|*[!0-9]*) ACC=0;; esac
  case "$REJ" in ''|*[!0-9]*) REJ=0;; esac
  NOW=$(date +%s)
  if [ "$MODE" = "ph" ]; then
    if ! pgrep -f 'wildrig-multi' >/dev/null 2>&1; then
      echo "C211_I121377_WR_NOT_RUNNING ts=$(ts) acc=$ACC rej=$REJ -> restart"
      EPI=$((EPI+1)); start_ph
    elif [ "$ACC" -eq 0 ] && [ $((NOW-PHSTART)) -ge 900 ]; then
      echo "C211_I121377_FALLBACK ts=$(ts) reason=NO_ACCEPTED_SHARE_900S mode=lp_sticky"
      pkill -9 -f wildrig-multi >/dev/null 2>&1
      MODE=lp
      if install_srb; then start_srb; else echo "C211_I121377_SRB_UNAVAILABLE_RETRY_NEXT"; fi
    fi
  else
    if ! pgrep -f 'srbminer' >/dev/null 2>&1; then
      echo "C211_I121377_SRB_NOT_RUNNING ts=$(ts) -> restart"
      if [ ! -x $D/srbminer ]; then install_srb; fi
      start_srb
    fi
    ACC=$(grep -ciE 'accepted' $D/srb.log 2>/dev/null || true); case "$ACC" in ''|*[!0-9]*) ACC=0;; esac
  fi
  HB=$((HB+1))
  if [ "$HB" -ge 10 ]; then HB=0; hb; fi
done
