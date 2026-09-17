# Verificator de Plagiat

Aplicație web construită cu Flask care verifică similaritatea unui document față de surse de pe internet.

Încarcă un fișier (`.docx`, `.pdf` sau `.txt`) și aplicația:

1. Extrage textul brut din document.
2. Selectează aleatoriu mai multe fraze de 5–10 cuvinte.
3. Caută fiecare frază pe internet prin instanța locală **SearXNG**.
4. Descarcă și curăță paginile din rezultatele căutării.
5. Compară fiecare frază cu textul paginilor găsite, calculând un scor de similaritate.
6. Afișează un procentaj general de similaritate, un nivel de risc și frazele care s-au potrivit, cu linkuri către sursele originale.
7. Permite descărcarea unui raport PDF cu rezultatele.

## Cerințe preliminare

- O instanță [SearXNG](https://searxng.github.io/searxng/) care rulează local (implicit pe `http://localhost:8080`) — aceasta este folosită ca motor de căutare; nu este necesară nicio cheie API externă.


### Teste

Testele folosesc backend-uri simulate (fără apeluri reale la rețea) pentru a verifica logica pipeline-ului: extragerea frazelor, agregarea rezultatelor, generarea PDF-ului și comportamentul rutelor.

## Niveluri de risc

Procentajul general de similaritate este calculat ca: `(fraze potrivite / total fraze verificate) × 100`.

| Nivel | Prag |
|---|---|
| Scăzut | Sub 20% |
| Mediu | 20% – 49% |
| Ridicat | 50% sau mai mult |

## Limitări cunoscute

- **Cache în memorie:** rapoartele generate sunt stocate în memoria procesului și se pierd la repornire. Pentru producție, înlocuiți cu o bază de date sau Redis.
- **Robustețea scraper-ului:** site-urile cu JavaScript intens sau cu paywall nu vor returna text utilizabil dintr-un simplu request HTTP. 
