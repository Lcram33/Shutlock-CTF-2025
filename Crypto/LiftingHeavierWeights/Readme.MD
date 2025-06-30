# Lifting Heavier Weights

![challenge](challenge.png)

## Prérequis

(Optionnel, recommandé) Vérifier les sommes de contrôle.
```bash
sha256sum -c SHA256SUMS.txt
```

## Remarque

En ajoutant une définition de variable dans out.txt et en renommant le fichier en `out.py`, on peut directement importer le flag chiffré dans le programme principal. C'est ce que j'ai fait ici.

<h2>Solution</h2>

<details>
<summary></summary>

Il s’agit d'une version modifiée du challenge précédent. Cette fois, $f$ est la **valeur p-adique**.
$$f(t) = v_p(t)$$

On utilise la propriété suivante :
$$v_p(x^n - y^n) =v_p(x - y) + v_p(n)$$

Or : $v_p(x-y) = first$ et $v_p(n) = byte \cdot big\_big\_big$

D'où : $v_p(x^n - y^n) = first + byte \cdot big\_big\_big$

Ainsi : $v_p(x^n - y^n) - first = byte \cdot big\_big\_big$

Ou, écrit autrement : $f(p, temp) - first = byte \cdot big\_big\_big$

On peut alors récupérer chaque octet du flag par division euclidienne successive par 1000, en effet, en notant $b_i$ l'octet $i$ du flag, on a :

$$S = b_0 + b_1 \cdot 1000^1 + b_2 \cdot 1000^2 + \text{...}$$


Flag : `SHLK{C4us3_B4by_Y0ur3_4_F1r3w0rk}`