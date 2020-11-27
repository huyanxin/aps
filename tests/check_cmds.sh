#!/usr/bin/env bash

# Copyright 2020 Jian Wu
# License: Apache 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

set -eu

for x in am lm ss; do python ../bin/train_$x.py -h; done
for x in am ss; do python ../bin/distributed_train_$x.py -h; done
for x in wer ss_metric gmvn; do python ../bin/compute_$x.py -h; done
for x in separate_blind decode decode_batch; do python ../bin/$x.py -h; done

# 5.12% & 2.70%
for cer in true false; do
  ../bin/compute_wer.py --cer $cer data/metric/asr/hyp.en.text \
    data/metric/asr/ref.en.text
  ../bin/compute_wer.py --cer $cer data/metric/asr/hyp.zh.text \
    data/metric/asr/ref.zh.text
done

for metric in sdr pesq stoi sisnr; do
  ../bin/compute_ss_metric.py --metric $metric \
    data/metric/sse/bss_spk1.scp,data/metric/sse/bss_spk2.scp \
    data/metric/sse/ref_spk1.scp,data/metric/sse/ref_spk2.scp
done

../bin/compute_gmvn.py --transform asr --sr 16000 \
  data/dataloader/ss/wav.1.scp data/transform/transform.yaml /dev/null

# test decoding for att
cpt_dir=data/checkpoint/aishell_att_1a
../bin/decode.py $cpt_dir/egs.scp - \
    --beam-size 24 \
    --checkpoint $cpt_dir \
    --device-id -1 \
    --channel -1 \
    --dict $cpt_dir/dict \
    --max-len 50 \
    --normalized true \
    --vectorized true \

../utils/wav_duration.py --output sample data/dataloader/ss/wav.1.scp -
../utils/archive_wav.py data/dataloader/ss/wav.1.scp /dev/null

head data/metric/asr/ref.en.text | ../utils/tokenizer.pl --space "<space>" -
../utils/tokenizer.py --space "<space>" --unit char --dump-vocab - \
  --text-format kaldi data/metric/asr/ref.en.text /dev/null
../utils/tokenizer.py --unit word --dump-vocab /dev/null --add-units "<sos>,<eos>,<unk>" \
  --text-format kaldi data/metric/asr/ref.zh.text -
../utils/tokenizer.py --spm data/checkpoint/en.libri.unigram.spm.model --unit subword \
  --text-format kaldi data/metric/asr/ref.en.text -
