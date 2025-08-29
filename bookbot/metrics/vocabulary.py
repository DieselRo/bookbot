from typing import Dict, Optional, Set

from .counts import get_word_counts

STOPWORDS_EN: Set[str] = {
    'a','about','above','after','again','against','all','am','an','and','any','are','as','at',
    'be','because','been','before','being','below','between','both','but','by','can','did','do',
    'does','doing','down','during','each','few','for','from','further','had','has','have','having',
    'he','her','here','hers','herself','him','himself','his','how','i','if','in','into','is','it',
    "it's",'its','itself','just','me','more','most','my','myself','no','nor','not','now','of','off',
    'on','once','only','or','other','our','ours','ourselves','out','over','own','same','she','should',
    'so','some','such','than','that','the','their','theirs','them','themselves','then','there','these',
    'they','this','those','through','to','too','under','until','up','very','was','we','were','what',
    'when','where','which','while','who','whom','why','will','with','you','your','yours','yourself',
    'yourselves','s','ll','re','ve','d','t'
}

def vocabulary_metrics(text: str, stopwords: Optional[Set[str]] = None) -> Dict[str, float]:
    counts = get_word_counts(text, stopwords=stopwords)
    tokens = sum(counts.values())
    types = len(counts)
    hapax = sum(1 for v in counts.values() if v == 1)
    dis = sum(1 for v in counts.values() if v == 2)
    ttr = (types / tokens) if tokens else 0.0
    return {
        "tokens": float(tokens),
        "types": float(types),
        "type_token_ratio": float(ttr),
        "hapax_legomena": float(hapax),
        "hapax_ratio": float(hapax / tokens) if tokens else 0.0,
        "dis_legomena": float(dis),
        "dis_ratio": float(dis / tokens) if tokens else 0.0,
    }

