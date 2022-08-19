from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import numpy as np
from loguru import logger
from text_renderer.utils.errors import PanicError
from text_renderer.utils.utils import random_choice

from .corpus import Corpus, CorpusCfg


@dataclass
class OrderCorpusCfg(CorpusCfg):
    """
    顺序采样的配置

    args:
        text_paths (List[Path]): Text file paths
        items (List[str]): Texts to choice. Only works if text_paths is empty
        filter_by_chars (bool): If True, filtering text by character set
        chars_file (Path): Character set
        filter_font (bool): Only work when filter_by_chars is True. If True, filter font file
                            by intersection of font support chars with chars file
        filter_font_min_support_chars (int): If intersection of font support chars with chars file is lower
                                             than filter_font_min_support_chars, filter this font file.

    """

    text_paths: List[Path] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    filter_by_chars: bool = False
    chars_file: Path = None
    filter_font: bool = False
    filter_font_min_support_chars: int = 100


class OrderCorpus(Corpus):
    """
    按顺序采样
    """

    def __init__(self, cfg: "CorpusCfg"):
        super().__init__(cfg)

        self.cfg: OrderCorpusCfg
        if len(self.cfg.text_paths) == 0 and len(self.cfg.items) == 0:
            raise PanicError(f"text_paths or items must not be empty")

        if len(self.cfg.text_paths) != 0 and len(self.cfg.items) != 0:
            raise PanicError(f"only one of text_paths or items can be set")

        self.texts: List[str] = []

        if len(self.cfg.text_paths) != 0:
            for text_path in self.cfg.text_paths:
                with open(str(text_path), "r", encoding="utf-8") as f:
                    for line in f.readlines():
                        self.texts.append(line.strip())

        elif len(self.cfg.items) != 0:
            self.texts = self.cfg.items

        if self.cfg.chars_file is not None:
            self.font_manager.update_font_support_chars(self.cfg.chars_file)

        if self.cfg.filter_by_chars:
            self.texts = Corpus.filter_by_chars(self.texts, self.cfg.chars_file)
            if self.cfg.filter_font:
                self.font_manager.filter_font_path(
                    self.cfg.filter_font_min_support_chars
                )

        self.text_count = len(self.texts)
        self.sample_count = 0

    def get_text(self):
        text = self.texts[self.sample_count % self.text_count]
        self.sample_count+=1
        return text
