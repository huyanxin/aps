# Copyright 2018 Jian Wu
# License: Apache 2.0 (http://www.apache.org/licenses/LICENSE-2.0)

from collections import defaultdict
from typing import Optional, NoReturn
from kaldi_python_io import Reader as BaseReader


class MetricReporter(object):
    """
    Metric reporter (WER, SiSNR, SDR ...)
    """

    def __init__(self,
                 spk2class: Optional[str] = None,
                 name: str = "UNK",
                 unit: str = "UNK") -> None:
        self.s2c = BaseReader(spk2class) if spk2class else None
        self.val = defaultdict(float)
        self.name = name
        self.unit = unit

    def report(self):
        """
        Print results
        """
        raise NotImplementedError


class AverageReporter(MetricReporter):
    """
    Reportor for SDR, PESQ, SiSNR
    """

    def __init__(self,
                 spk2class: Optional[str] = None,
                 name: str = "UNK",
                 unit: str = "UNK") -> None:
        super(AverageReporter, self).__init__(spk2class=spk2class,
                                              name=name,
                                              unit=unit)
        self.cnt = defaultdict(int)

    def add(self, key: str, val: float) -> NoReturn:
        cls_str = "NG"
        if self.s2c:
            cls_str = self.s2c[key]
        self.val[cls_str] += val
        self.cnt[cls_str] += 1

    def report(self) -> NoReturn:
        print(f"{self.name} ({self.unit}) Report: ")
        tot_utt = sum([self.cnt[cls_str] for cls_str in self.cnt])
        tot_snr = sum([self.val[cls_str] for cls_str in self.val])
        print(f"Total: {tot_snr / tot_utt:.3f}, {tot_utt:d} utterances")
        if len(self.val) != 1:
            for cls_str in self.val:
                cls_snr = self.val[cls_str]
                num_utt = self.cnt[cls_str]
                print(f"\t{cls_str}: {cls_snr / num_utt:.3f}, " +
                      f"{num_utt:d} utterances")


class WerReporter(MetricReporter):
    """
    Reportor for WER, CER
    """

    def __init__(self,
                 spk2class: Optional[str] = None,
                 name: str = "UNK",
                 unit: str = "UNK") -> None:
        super(WerReporter, self).__init__(spk2class=spk2class,
                                          name=name,
                                          unit=unit)
        self.tot = defaultdict(float)
        self.cnt = 0

    def add(self, key: str, val: float, tot: int) -> NoReturn:
        cls_str = "NG"
        if self.s2c:
            cls_str = self.s2c[key]
        self.val[cls_str] += val
        self.tot[cls_str] += tot
        self.cnt += 1

    def report(self) -> NoReturn:
        print(f"{self.name} ({self.unit}) Report: ")
        sum_err = sum([self.val[cls_str] for cls_str in self.val])
        sum_len = sum([self.tot[cls_str] for cls_str in self.tot])
        print(f"Total: {sum_err * 100 / sum_len:.2f}{self.unit}, " +
              f"{self.cnt} utterances ({sum_err} errors, {sum_len} units)")
        if len(self.val) != 1:
            for cls_str in self.val:
                cls_err = self.val[cls_str]
                cls_tot = self.tot[cls_str]
                print(f"  {cls_str}: {cls_err * 100 / cls_tot:.2f}{self.unit}")
