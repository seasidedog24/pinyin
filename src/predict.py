import math
from . import train


def predict(py_text: str, alpha: float = 1e-7, epsilon: float = 1e-233) -> str:
    """Predict character sequence from whitespace-separated pinyin tokens.

    Args:
        py_text: whitespace-separated pinyin string
        alpha: interpolation weight for unigram vs bigram (0..1)
        epsilon: tiny smoothing constant (must be > 0)

    Returns:
        Predicted character string (or empty string if prediction is not possible).
    """
    if not isinstance(py_text, str):
        raise TypeError("py_text must be a string")

    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha must be between 0 and 1")
    if not (epsilon > 0.0):
        raise ValueError("epsilon must be positive")

    # tokenize and remove any empty tokens
    py_list = [tok for tok in py_text.split() if tok]
    if not py_list:
        return ""

    one_word = getattr(train, "prob_one_word", None)
    two_word = getattr(train, "prob_two_word", None)
    if not isinstance(one_word, dict) or not isinstance(two_word, dict):
        raise RuntimeError("train.prob_one_word and train.prob_two_word must be dicts")

    def unigram_prob(py: str, word: str) -> float:
        return float(one_word.get(py, {}).get(word, 0.0))

    def bigram_prob(prev: str, curr: str) -> float:
        # original implementation concatenated words as key
        return float(two_word.get(prev + curr, 0.0))

    # Initialize Viterbi-like structures
    first_py = py_list[0]
    first_candidates = one_word.get(first_py)
    if not first_candidates:
        return ""

    path = {}
    f_prev = {}
    for word, p in first_candidates.items():
        score = math.log(max(float(p), epsilon))
        path[word] = word
        f_prev[word] = score

    # Iterate through remaining pinyin tokens
    for py in py_list[1:]:
        candidates = one_word.get(py)
        if not candidates:
            # no candidates for this token — cannot continue reliably
            return ""

        f_cur = {}
        new_path = {}

        for prev_word, prev_score in f_prev.items():
            for curr_word in candidates:
                pu = unigram_prob(py, curr_word)
                pb = bigram_prob(prev_word, curr_word)
                interp = alpha * pu + (1.0 - alpha) * pb
                score = prev_score + math.log(max(interp, epsilon))

                # update best score and path for curr_word
                if score > f_cur.get(curr_word, -math.inf):
                    f_cur[curr_word] = score
                    new_path[curr_word] = path[prev_word] + curr_word

        # if no transitions are possible, abort
        if not f_cur:
            return ""

        f_prev, path = f_cur, new_path

    # choose the best final candidate
    best_token = max(f_prev.items(), key=lambda kv: kv[1])[0]
    return path.get(best_token, "")
