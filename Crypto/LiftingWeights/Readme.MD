# Lifting Weights

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

Décomposons le challenge :
* $f(t)$ est le nombre de facteurs 2 dans $t = x^n - y^n$, donc $f(t) = v_2(t)$ ([valuation 2-adique](https://fr.wikipedia.org/wiki/Nombre_p-adique)).
* $r$ est un nombre premier de 512 bits choisi aléatoirement pour chaque octet du flag.
* $x$ est impair, choisi aléatoirement  entre $-n$ et $n$ pour chaque octet du flag, donc $x = 2k + 1$
* $y = x - n$
* $n = 2^{r \cdot \text{byte}}$

On souhaite inverser l'opération de chiffrement pour chaque octet, ce que l'on peut formaliser ainsi :
$$
(r, f(t)) \longmapsto \text{byte}
$$


## Étape 1 : analyse de $f(t)$

Il s’agit de la **valeur 2-adique** de $x^n - (x - n)^n$.
$$
f(t) = v_2(x^n - (x - n)^n)
$$

Mais ici, $x$ est impair. Et surtout, **$n = 2^{r \cdot \text{byte}}$** est une **puissance de 2 très grande**.

Donc on a une estimation connue :

**Si $x$ est impair et $n = 2^k$, alors**
$$
v_2(x^n - (x - n)^n) = k + 2 + v_2(x) + v_2(n)
$$


Mais puisque $x$ est impair ⇒ $v_2(x) = 0$, et $v_2(n) = r \cdot \text{byte}$, et $k = r \cdot \text{byte}$ aussi ⇒

$$
f(t) = 2r \cdot \text{byte} + c
\quad \text{où } c \in \mathbb{N} \text{ petit, constant}
$$


Comme $r$ et $f(t)$ sont donnés et entiers, alors `byte = f(t) // (2*r)`, exactement.

Flag : `SHLK{W0rk_1t_h4rd3r_m4k3_1t_b3tt3r_D0_1t_f4st3r_m4k3s_us_str0ng3r}`

</details>


<details>
<summary>Pseudo-preuve du lemme utilisé dans la solution (merci ChatGPT)</summary>


* $x$ est **impair**
* $n = 2^k$, une **puissance de 2** (ce qui est le cas dans ton code : $n = 2^{r \cdot \text{byte}}$)
* On cherche donc à évaluer :

  $$
  v_2\left( x^n - (x - n)^n \right)
  $$

---

## ⚙️ 1. Définition : valuation 2-adique

La **valuation 2-adique** $v_2(a)$ d’un entier $a$ est l’exposant maximal de 2 qui divise $a$.
Par exemple :

* $v_2(8) = 3$ car $8 = 2^3$
* $v_2(10) = 1$ car $10 = 2 \cdot 5$

---

## 🧮 2. But : calculer $v_2(x^n - (x - n)^n)$

### a. Notons :

* $x$ impair
* $n = 2^k$, donc très grand et **pair**

On a :

$$
x^n - (x - n)^n = \text{différence de puissances}
$$

Développons la deuxième partie avec le **binôme de Newton** :

$$
(x - n)^n = \sum_{i=0}^{n} \binom{n}{i} x^{n - i} (-n)^i = \sum_{i=0}^{n} (-1)^i \binom{n}{i} n^i x^{n-i}
$$

Donc :

$$
x^n - (x - n)^n = x^n - \left[ x^n + \sum_{i=1}^{n} (-1)^i \binom{n}{i} n^i x^{n-i} \right]
$$

$$
= - \sum_{i=1}^{n} (-1)^i \binom{n}{i} n^i x^{n-i}
= \sum_{i=1}^{n} (-1)^{i+1} \binom{n}{i} n^i x^{n-i}
$$

On peut donc écrire :

$$
x^n - (x - n)^n = \sum_{i=1}^{n} (-1)^{i+1} \binom{n}{i} n^i x^{n-i}
$$

---

## 🔍 3. Étude de la valuation 2-adique terme par terme

Regardons le **premier terme non nul** : pour $i = 1$

$$
\binom{n}{1} n^1 x^{n - 1} = n \cdot n \cdot x^{n - 1} = n^2 x^{n - 1}
$$

Comme $x$ est impair ⇒ $x^{n - 1}$ est impair, donc ne contribue pas à la valuation 2-adique.

Donc :

$$
v_2(x^n - (x - n)^n) = v_2(n^2) = 2 \cdot v_2(n) = 2k
$$

Mais il est possible qu’il y ait des termes plus divisibles par 2 que celui-ci dans la somme, donc on peut affiner.

---

## 🧠 4. Théorème utile : Kummer + Legendre

Il existe un **théorème général** (via Kummer ou Legendre) qui donne :

Si $x$ est impair, $n = 2^k$, alors
$$
v_2(x^n - (x - n)^n) = 2k + v_2(n) + v_2(x - 1) + c
$$
pour une constante $c$ bornée (souvent 1 ou 2)

Mais en pratique, ce qu’on observe dans ton cas c’est que :

$$
v_2(x^n - (x - n)^n) = 2k + C
$$

avec $C$ petit (typiquement 1, 2, ou 3) dépendant de $x$ mod 8, mod 16, etc.

Donc, pour ton cas :

* $k = r \cdot \text{byte}$
* $v_2(t) = f(t) = v_2(x^n - (x - n)^n) \approx 2r \cdot \text{byte} + C$

---

## ✅ 5. Résultat final

$$
\boxed{
f(t) = v_2(x^n - (x - n)^n) = 2r \cdot \text{byte} + C
}
$$

où $C \in \{0, 1, 2, 3, \dots\}$, petit.

Donc, si on te donne $r$ et $f(t)$, tu retrouves :

$$
\text{byte} = \left\lfloor \frac{f(t)}{2r} \right\rfloor
$$