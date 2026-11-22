# on the RunPod exec pod (tools/runpod_exec.py): install basics, fetch ACE-Step 1.5 code and docs, dump what we need to read
set -x
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null && apt-get install -y -qq git ffmpeg curl >/dev/null
nvidia-smi; python3 --version; nproc; df -h /w | tail -1
cd /w && rm -rf acestep && git clone --depth 1 https://github.com/ace-step/ACE-Step-1.5 acestep || git clone --depth 1 https://github.com/ACE-Step/ACE-Step-1.5 acestep
mkdir -p /w/out/docs
cd /w/acestep && git log -1 --format='%H %cd' && ls -la
cp README.md /w/out/docs/README.md 2>/dev/null
cp LICENSE* /w/out/docs/ 2>/dev/null
find . -maxdepth 3 \( -name "*.md" -o -name "pyproject.toml" -o -name "requirements*.txt" -o -name "setup.py" \) -not -path "./.git/*" | head -80 > /w/out/docs/files.txt
cp pyproject.toml requirements*.txt /w/out/docs/ 2>/dev/null
for f in $(find . -maxdepth 3 -name "*.md" -not -path "./.git/*" | grep -i -E "infer|api|cli|usage|guide|tutorial|en" | head -12); do cp --parents "$f" /w/out/docs/ ; done
find . -maxdepth 3 -name "*.py" -not -path "./.git/*" | grep -i -E "infer|cli|generate|api|main|run" | head -40 > /w/out/docs/py_entry.txt
curl -sL https://huggingface.co/ACE-Step/Ace-Step1.5/raw/main/README.md -o /w/out/docs/hf_Ace-Step1.5.md
ls -la /w/out/docs
