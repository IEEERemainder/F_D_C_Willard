import itertools

class TypesStorage: # no need to generate, i'm just crazy, babe
    def __init__(self):
        pass

    def mbti():
        return ["".join(["IE"[i & 1 > 0], "SN"[i & 2 > 0], "TF"[i & 4 > 0], "JP"[i & 8 > 0]]) for i in range(16)] # TODO: change order of types?
    
    def enneagram():
        return [f"{1 + i // 2}w{(i // 2 + (1 if i & 1 else 8)) % 9 + 1}" for i in range(18)]
    
    def tritypes():
        return [f[i % 3] + s[i // 3 % 3] + t[i // 9] for (f, s, t) in itertools.permutations(["891", "234", "567"]) for i in range(3 ** 3)] # same as in types_mbti
    
    def socionics():
        return [f + s + "IE"[i&1] for (i, (f, s)) in zip(range(16), [(x, y) for (x, y, z, w) in itertools.permutations("ISEL") if not scan(["IS", "EL"], lambda a: x in a and y in a)])]
    
    def attitudialPsyche():
        return ["".join(x) for x in itertools.permutations("VLEF")]
    
    def instincts():
        return set([f"s{x}/s{y}" for (x, y, _) in itertools.permutations("xpo")])