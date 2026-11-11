> **Porijeklo i granice dokumenta**
> Datum: 10.11.2026, UTC. Kod: `132ef288917b0573709655437cb8904574898015`, grana `implementation/mevan-paket-2-20261110`, lokalni paket 2. Read-only potvrđeni HEAD i čisto radno stablo; nema fetch/push/PR/deploy akcije tokom dokumentovanja.
> Primarni izvor: stvarni izvorni kod tog commita; dodatno postojeći registri, korisničke poruke i sačuvani QA logovi. Opseg: svi ekrani, statičke/dinamičke kontrole, layout i izvozi.
> Sve reference `datoteka:linija` važe samo za navedeni commit i relativne su korijenu njegovog izvornog koda. Putanje u dokumentima vode do dokumentacije/inventara u ovom paketu, ne do produkcije.
> Starija historija i prilozi nisu potpuni. D-001–D-100 i CSV 366 ankera nisu dostupni. Izvorni chat je pročitao podijeljeni razgovor; ovo cloud okruženje ga nije uspješno pročitalo. Razgovor nije dokaz implementacije. Stvarni AI, Render i udaljeni PostgreSQL nisu novo testirani. Dokumentovanje ne proglašava lokalne funkcije objavljenim.

# MEVAN — specifikacija interfejsa i interakcija

## Svrha i jezik

Nastavlja se postojeći interfejs bez općeg redizajna. Važeća odluka: prva verzija samo bosanski; engleski je kasnija faza. HTML lang=bs i većina akcija/izvještaja jesu bosanski, ali postoje stari „Operational & Business Performance Transformation”, „PRIVATE DEMO”, „Portfolio dashboard”, „Project Charter”, „Decision Intelligence”, engleske kategorije/stanja i schema ključevi. To nije završena lokalizacija. Interni JSON/API ključevi ostaju kompatibilni; ne prevoditi ih neplanirano.

## Layout i dizajn

`index.html:2`: svijetla pozadina#f 3 f 6 fa, osnovni tekst#193047, tamnoplavi header#142 e 46, bijeli paneli s rubom#dfe 7 ef i radius 14, primarna akcija#0 a 6485, progress tirkizna#159786, warning#fff 4 dc/#995600. Font Inter s system fallbackom; ne povlači Google font servis. Desktop max-width 1200, sidebar 245 px+ostatak, gap 20; grid 3 i two 2 kolone. Breakpoint 750 px spušta sidebar/layout na jednu kolonu, stat grid 2, forme jedna kolona. Backup panel na<=760 px ima position:static, da ne prekriva akcije. Print skriva header/nav/controls i rubove panela. To su stvarne CSS vrijednosti, ne zaseban usvojeni dizajn sistem.

Projektni ekran je zaseban HTML s vlastitim panel/grid/structured formama; dashboard breakpoint 700 px; Guided ekran koristi details po kriteriju i prikazuje samo polja aktivnog koraka. Nema SPA router biblioteke, modal frameworka ni uniformne globalne state mašine. Dugmad često rade confirm/alert/prompt; greške su inline status ili alert. Accessibility djelimično: lang/label i aria-live/status/alert; dynamic field na Guided ima aria-label; nije potpuni WCAG audit.

## Mapa ekrana i uslova

| Ekran / prikaz | Pristup i ulazi | Obrada / izlaz | Validacije, greške i uslovi |
|---|---|---|---|
| `/login` | Javno; e-mail, password, hidden csrf_token | POST/login, 8 h sesija, 303 | required/email HTML; server token 15 min, pogrešno 401, limit 429 |
| `/` radni prostor | Sesija; company/diagnostic selekcija, dodaj/preimenuj | JSON workspace, aktivni kontekst | prompt/confirm; localStorage i cloud CAS; conflict ne prepisuje |
| Profil kompanije | name, industry, employees, revenue, location, erp, contact | Čuva postojeći company JSON | Nema billing/CRM ili registracije; slaba serverska semantička provjera profila |
| Pregled dijagnostike | Trenutni assess | ukupni/modularni indeks, coverage, quality/cross-check | nepoznato≠0; N/P opravdanje; upozorenje na razliku>=3 u F06/O05, F05/O01, P01/P02 |
| Pet modula F/O/P/L/M | Svih 61 pitanja, score, proof, applicable, nalaz/dokaz/KPI/finansija/preporuka | Jedan kriterij ili cijeli modul; prethodni/sljedeći | confirmed zahtijeva score/evidence; N/P razlog/konsultant; upozorenja nisu nezavisna provjera |
| Finansijski registar | Do 200 scenario efekata; category, annual, oneoff, overlap, evidence/status/osnovica/cilj/unit/period | Rule analiza i finansijsko razdvajanje | Nema automatske potvrde novca; METALPRO iznosi samo izvorni primjer |
| Integrisana analiza v2/v3 | assess, effects, company | Pravila, generativni tekst ili strukturirani AI facts+analysis | Bez ključa 503; status poruke; network/format greške ne odobravaju ništa |
| Analiza i odobravanje | modul/ALL, uređeni nacrt | Legacy interno simulacijsko odobrenje, fingerprint ulaza/teksta | Potvrda samo za interni demo; promjena teksta/ulaza poništava status; nije novi finalni gate |
| Izvještaji | Modul/ALL × kratko/detaljno | Browser popup print/PDF i ručni DOCX | Popup blocker poruka; radni nacrti, N/P razlozi, DEMO label; ne zamjenjuje zaključani download |
| Plan 90 dana | task, owner, due, kpi, status; dodaj/ukloni | Legacy plan lista | Nije isti tip kao Guided month 1–3 ili project activities; očuvati paralelne podatke |
| Podaci/sigurnost | JSON import/export i lokalno brisanje | Browser kopija; odvojene serverske backup akcije | lokalno brisanje≠server delete; import strukturna provjera; restore destruktivan uz potvrde |
| `/diagnostic-review` | Sesija + sessionStorage mevan-review-selection | Radni TEST workspace, stage, gate i approvals | Bez selection poruka za povrat; stale 409; stvarna promjena ulaza traži confirm, stari snimci ostaju |
| `/projects-ui` | Sesija; company/diagnostic/title, analysis JSON | Kandidati/rating/nacrt/projekat/scenariji/weeklies/efekti/izvozi | Statusno zaključavanje; server auth/origin; posebno ispod |
| `/dashboard-ui` | Sesija; company/status filter | Read-only portfolio/statistika/rokovi | Nema iznosa različitih perioda u jednoj sumi; zakasnjelo ne znači nezavršeno |

## Guided koraci i polja

1. Intervju: odvojena tekstualna bilješka za svaki kriterij, sačuvaj/nastavi. 2. Dokumenti: odvojena referenca/bilješka, bez uploada. 3. Obilazak: zasebno opažanje. 4. Dokazi: status, score 0–5/prazno, evidence_reference, source_id, assessor_id, period start/end, assessment_version, timestamp, verification_audit_ref, na_reason, na_approved_by; dugme potvrde N/P koristi prijavljenog reviewer-a. Provjera rizika O14/L09/M08 je u ovom koraku. 5. Prioriteti: summary i priority 1–3. 6. Projekat: izaberi prvi/drugi/treći prioritet C1/C2/C3, owner, start date, kpi; kreiranje nacrta traži i sva tri perioda plana, pa korisnik može otići na korak 7 i vratiti se. 7. Plan: month 1–3, opis aktivnosti/vlasnika/KPI/roka.

Pritiskom „Sačuvaj i nastavi” snima se trenutna revizija i novi korak; sam izbor koraka je radno stanje do spremanja. „Sačuvaj radnu reviziju” ne odobrava; „Odobri pregledanu reviziju” ili „Zaključi DEMO snimak” traži confirm, sprema pa poziva gate. Tok nije strogo linearna blokada svakog prelaska: korisnik može navigirati, a finalni gate blokira nepotpunost. Missing panel prikazuje liste kriterija/nedostajuća polja za odabrani korak, ali nije stručna ocjena sadržaja.

Režim se bira eksplicitno real/demo. METALPRO demo seed vidljiv je samo rezervnom company id-u; popunjava prazna source/review polja i simulacijske statuse. Režim poruka i approval akcije stalno razlikuju simulaciju od stvarnog nalaza. Čitanje liste starih snimaka dostupno je i kada novi pregled nije pokrenut. Projekat drugog režima ne može se povezati; postojeći odgovarajući projekat traži confirm bez prepisivanja.

## Projektne forme i uslovne akcije

Kandidati: analiza JSON, company/diagnostic ID, dugme učitaj kandidate; po kandidatu pet faktor select 0–5, obrazloženje i evidence IDs; rangiraj, učitaj/sačuvaj ocjene na serveru, izaberi kandidat za deterministički/AI pack. UI obrazloženje>=15, server rank>=5; incomplete petorka odbijena u UI, server vraća nedostajuće ocjene. Učitavanje PG/SQLite nacrta čuva reviziju, ne prepisuje konflikt 409.

Kreiranje projekta: title, problem, objective, scope, methodology, assumptions/checks red-po-red; tri bool potvrde; strukturirane activities(title, owner, deadline, deliverable, acceptance_criteria) i kpis(name, formula, source, baseline, target, owner, frequency), dodaj/ukloni; financial_effects JSON tekst. draft/validation editable, implementation zaključava charter i financial-model. DEMO project režim se čuva i na save; backend ne dopušta implementaciju, iako stari UI i dalje ima opće implementacijsko dugme (greška 409 objašnjava).

Scenariji: tri panela s capex/running cost, listom koristi(name, category, amount, source, assumption); preview i save; samo estimated. Weeklies vidljivi samo implementation: ISO week, aktivnosti s statusom not_started/in_progress/done/blocked, KPI measurements, blockers, decisions, note. Actuals panel samo implementation: period, name, category, amount, evidence, calculation_note, source_owner, consultant_confirmed i opcionalni eventkey; key/sadržaj treba ostati isti pri retry. Izvoz projekta PDF/DOCX je zaseban od dijagnostičkog izvještaja. Audit se čita API-jem; nema zasebnog punog audit admin ekrana.

## Izvoz i statusi dokumenata

Tri paralelna dijagnostička izvoza ostaju: ručni Word/print nacrt s glavnog ekrana, v3 strukturirani radni Word, te server-approved bound snapshot u četiri varijante. Postoje i projektni PDF/DOCX. Legacy Word koristi vlastiti ZIP/OOXML serializer bez biblioteke; server Word python-docx, PDF ReportLab+DejaVu. Snapshot v2 uključuje coverage/N/P, zamrznuti indeks i radar; v1 ne dobija retroaktivno novu sekciju. Radar se ne crta kada neki modul ima None; nije nulti poligon.

DEMO riječ je tačno „DEMO — simulirani podaci”; server PDF svaka stranica, DOCX header/footer i tijelo. Nije stvarno odobren/provjeren rezultat. URL mode=real ne mijenja već zaključani mode. Legacy štampa/nacrti nemaju istu kriptografsku vezu kao server snapshot. Odobreni stvarni dokument ne može biti proizveden od METALPRO simulacije kroz promjenu tog parametra.

Paket 2 ima vizuelno pregledane reprezentativne PDF stranice, uključujući radar/N/P/prazan skup; Word QA je strukturni/sadržajni. **Vizuelna Word/LibreOffice paginacija nije potvrđena.** Screenshoti ranijih dokaza su sintetički; ne uključuju se privatni login/dashboard podaci u ovu predaju.

## Potpuni statički inventar kontrola

217 unosa ispod pokriva sve pronađene button/input/select/textarea/a/form/option/summary tag definicije u svim praćenim HTML datotekama i loginu, uključujući string predloške, te literal createElement kontrole. To nije tvrdnja da statički scanner zna sve sadržaje dinamičkih petlji; polja iz field/FORM_FIELDS funkcija i uslovi su dodatno opisani gore. Po poljima s ID/data-field i source:line može se direktno nastaviti rad. Za option izlaz je izbor roditeljskog select-a; za input/textarea promjena radnog modela pa eksplicitni/debounced save; za button/a obrada je navedeni handler/href. Greške i auth nasljeđuju ugovor svog ekrana/API-ja. Nije izmišljeno dugme za nepostojeći billing ili user CRUD.

### Definicije iz `dashboard_ui.html`

| ID / izvor | Tip i oznaka/sadržaj | Ulaz / obrada / uslov |
| --- | --- | --- |
| UI-001 · dashboard_ui.html:3 | a · ← Upravljanje projektima | {"href": "/projects-ui"} |
| UI-002 · dashboard_ui.html:3 | a · Dijagnostika | {"href": "/"} |
| UI-003 · dashboard_ui.html:3 | select · Sve kompanije | {"id": "company"} |
| UI-004 · dashboard_ui.html:3 | option · Sve kompanije | {"value": ""} |
| UI-005 · dashboard_ui.html:3 | select · Svi statusi Nacrt Validacija Implementacija Zatvoreno | {"id": "status"} |
| UI-006 · dashboard_ui.html:3 | option · Svi statusi | {"value": ""} |
| UI-007 · dashboard_ui.html:3 | option · Nacrt | {"value": "draft"} |
| UI-008 · dashboard_ui.html:3 | option · Validacija | {"value": "validation"} |
| UI-009 · dashboard_ui.html:3 | option · Implementacija | {"value": "implementation"} |
| UI-010 · dashboard_ui.html:3 | option · Zatvoreno | {"value": "closed"} |
| UI-011 · dashboard_ui.html:5 | a · Dinamička kontrola: ).join(', '):'Nema datuma aktivnosti u prošlosti'; const link=document.createElement('a'); link.href='/projects-ui'; link.textContent='Otvori projektni modul'; card.append(h, sub, metrics, effects, due, link); el('projects').append(card)}} | JS createElement; broj instanci zavisi od podataka |
| UI-012 · dashboard_ui.html:6 | option · Dinamička kontrola: [...new Set(data.map(p=&gt;p.company_id))].sort()){const option=document.createElement('option'); option.value=company; option.textContent=company; el('company').append(option)}render()}catch(e){el('error').className='error'; el('error').textContent=e.message}}el('company').addEventListener('chan | JS createElement; broj instanci zavisi od podataka |


### Definicije iz `diagnostic_review.html`

| ID / izvor | Tip i oznaka/sadržaj | Ulaz / obrada / uslov |
| --- | --- | --- |
| UI-013 · diagnostic_review.html:6 | a · ← Dijagnostika | {"href": "/"} |
| UI-014 · diagnostic_review.html:10 | select · Stvarni konsultantski pregled DEMO — simulirani podaci | {"id": "reportMode"} |
| UI-015 · diagnostic_review.html:10 | option · Stvarni konsultantski pregled | {"value": "real"} |
| UI-016 · diagnostic_review.html:10 | option · DEMO — simulirani podaci | {"value": "demo"} |
| UI-017 · diagnostic_review.html:10 | button · Pripremi METALPRO DEMO primjer | {"id": "demoExample", "type": "button", "hidden": null} |
| UI-018 · diagnostic_review.html:11 | select · 1. Intervju 2. Dokumenti 3. Obilazak 4. Dokazi i ocjene 5. Tri prioriteta 6. Odabrani projekat 7. Plan za 90 dana | {"id": "guidedStage"} |
| UI-019 · diagnostic_review.html:11 | option · 1. Intervju | {"value": "interview"} |
| UI-020 · diagnostic_review.html:11 | option · 2. Dokumenti | {"value": "documents"} |
| UI-021 · diagnostic_review.html:11 | option · 3. Obilazak | {"value": "visit"} |
| UI-022 · diagnostic_review.html:11 | option · 4. Dokazi i ocjene | {"value": "evidence"} |
| UI-023 · diagnostic_review.html:11 | option · 5. Tri prioriteta | {"value": "priorities"} |
| UI-024 · diagnostic_review.html:11 | option · 6. Odabrani projekat | {"value": "project"} |
| UI-025 · diagnostic_review.html:11 | option · 7. Plan za 90 dana | {"value": "plan"} |
| UI-026 · diagnostic_review.html:11 | button · Sačuvaj i nastavi | {"id": "nextStage", "type": "button"} |
| UI-027 · diagnostic_review.html:14 | button · Preuzmi AI prijedlog za pregled | {"id": "useDraft", "hidden": null, "type": "button"} |
| UI-028 · diagnostic_review.html:15 | select · Prvi prioritet Drugi prioritet Treći prioritet | {"id": "projectChoice"} |
| UI-029 · diagnostic_review.html:15 | option · Prvi prioritet | {"value": "C1"} |
| UI-030 · diagnostic_review.html:15 | option · Drugi prioritet | {"value": "C2"} |
| UI-031 · diagnostic_review.html:15 | option · Treći prioritet | {"value": "C3"} |
| UI-032 · diagnostic_review.html:15 | input · projectOwner | {"id": "projectOwner"} |
| UI-033 · diagnostic_review.html:15 | input · projectStart | {"id": "projectStart", "type": "date"} |
| UI-034 · diagnostic_review.html:15 | textarea ·  | {"id": "projectKpi"} |
| UI-035 · diagnostic_review.html:15 | button · Sačuvaj odabrani projektni nacrt | {"id": "createGuidedProject", "type": "button"} |
| UI-036 · diagnostic_review.html:16 | button · Sačuvaj radnu reviziju | {"id": "save"} |
| UI-037 · diagnostic_review.html:16 | button · Odobri pregledanu reviziju | {"id": "approve"} |
| UI-038 · diagnostic_review.html:42 | a · Dinamička kontrola:  const link=document.createElement('a'); link.href=base+'/approvals/'+a.approval_id+'/'+view+'/'+fmt; link.textContent=label+' '+fmt.toUpperCase(); nav.append(link);} | JS createElement; broj instanci zavisi od podataka |
| UI-039 · diagnostic_review.html:78 | summary · Dinamička kontrola: eateElement('details'); details.dataset.code=code; const title=document.createElement('summary'); title.textContent=code+' · '+name+' · '+(record.score??'—')+'/5'; details.append(title); | JS createElement; broj instanci zavisi od podataka |
| UI-040 · diagnostic_review.html:88 | button · Dinamička kontrola:  const confirmNa=document.createElement('button'); confirmNa.type='button'; confirmNa.textContent='Potvrdi N/P kao prijavljeni konsultant'; confirmNa.onclick=()=&gt;{if(record.verification_status!=='nije_primjenjivo'){get('notice').textContent='Prvo od | JS createElement; broj instanci zavisi od podataka |
| UI-041 · diagnostic_review.html:180 | a · Dinamička kontrola:  if(diagnostic.guided.project_id){const a=document.createElement('a'); a.href='/projects-ui'; a.textContent='Projektni nacrt je sačuvan · '+diagnostic.guided.project_id; box.append(a)} | JS createElement; broj instanci zavisi od podataka |


### Definicije iz `index.html`

| ID / izvor | Tip i oznaka/sadržaj | Ulaz / obrada / uslov |
| --- | --- | --- |
| UI-042 · index.html:4 | form · Odjava | {"method": "post", "action": "/logout"} |
| UI-043 · index.html:4 | button · Odjava | {"class": "btn secondary", "type": "submit"} |
| UI-044 · index.html:4 | button · MEVAN 4.0 · Projekti TEST | {"type": "button", "onclick": "location.href='/projects-ui'"} |
| UI-045 · index.html:4 | button · Vođeno prikupljanje i završni izvještaji | {"type": "button", "onclick": "openDiagnosticReview()"} |
| UI-046 · index.html:4 | button · Kompanije i dijagnostike | {"data-page": "workspace"} |
| UI-047 · index.html:4 | button · Profil kompanije | {"data-page": "company"} |
| UI-048 · index.html:4 | button · Pregled dijagnostike | {"data-page": "overview"} |
| UI-049 · index.html:4 | button · Registar finansijskih efekata | {"data-page": "finance"} |
| UI-050 · index.html:4 | button · MEVAN 4.0 · Integrisana analiza | {"data-page": "v2"} |
| UI-051 · index.html:4 | button · Analiza i odobravanje | {"data-page": "review"} |
| UI-052 · index.html:4 | button · Izvještaji | {"data-page": "report"} |
| UI-053 · index.html:4 | button · Plan 90 dana | {"data-page": "plan"} |
| UI-054 · index.html:4 | button · Podaci i sigurnost | {"data-page": "data"} |
| UI-055 · index.html:50 | summary · Prikaži kriterije koje treba provjeriti (${q.missing.length}) | statički tag ili tag u JS predlošku |
| UI-056 · index.html:52 | summary · Jasna pravila ocjenjivanja za ${esc(c.code)} | statički tag ili tag u JS predlošku |
| UI-057 · index.html:88 | button · ${moduleName(d)} (${summary(CRITERIA.filter(c=&gt;c.dim===d)).valid}/${CRITERIA.filter(c=&gt;c.dim===d).length}) | {"data-page": "m:${esc(d)}"} |
| UI-058 · index.html:99 | button · + Novi finansijski nalaz | {"class": "btn", "onclick": "effects().push({id:'e'+Date.now(), name:'', category:'hard', annual: 0, oneoff: 0, overlap:'', evidence:'', status:'hypothesis'}); save(); render()"} |
| UI-059 · index.html:99 | input · name | {"data-effect": "${i}", "data-field": "name", "value": "${esc(x.name)}"} |
| UI-060 · index.html:99 | select · ${[['hard','Direktna ušteda'], ['avoidance','Izbjegnuti trošak'], ['contribution','Dodatna kontribucija'], ['working_capital','Oslobođeni obrtni kapital']].map(([v, l])=&gt;&#96; ${l} &#96;).join | {"data-effect": "${i}", "data-field": "category"} |
| UI-061 · index.html:99 | option · ${l} | {"value": "${v}", "${x.category": "==v?'selected':''}"} |
| UI-062 · index.html:99 | input · annual | {"type": "number", "min": "0", "data-effect": "${i}", "data-field": "annual", "value": "${Number(x.annual)\|\|0}"} |
| UI-063 · index.html:99 | input · oneoff | {"type": "number", "min": "0", "data-effect": "${i}", "data-field": "oneoff", "value": "${Number(x.oneoff)\|\|0}"} |
| UI-064 · index.html:99 | select · Hipoteza / nepotvrđeno U provjeri Stručno potvrđeno | {"data-effect": "${i}", "data-field": "status"} |
| UI-065 · index.html:99 | option · Hipoteza / nepotvrđeno | {"value": "hypothesis", "${x.status": "=='hypothesis'?'selected':''}"} |
| UI-066 · index.html:99 | option · U provjeri | {"value": "review", "${x.status": "=='review'?'selected':''}"} |
| UI-067 · index.html:99 | option · Stručno potvrđeno | {"value": "verified", "${x.status": "=='verified'?'selected':''}"} |
| UI-068 · index.html:99 | input · npr. loss 2 | {"data-effect": "${i}", "data-field": "overlap", "value": "${esc(x.overlap\|\|'')}", "placeholder": "npr. loss 2"} |
| UI-069 · index.html:99 | input · npr. 120 | {"type": "number", "step": "any", "data-effect": "${i}", "data-field": "baseline", "value": "${esc(x.baseline??'')}", "placeholder": "npr. 120"} |
| UI-070 · index.html:99 | input · target | {"type": "number", "step": "any", "data-effect": "${i}", "data-field": "target", "value": "${esc(x.target??'')}"} |
| UI-071 · index.html:99 | input · unit_value | {"type": "number", "step": "any", "data-effect": "${i}", "data-field": "unit_value", "value": "${esc(x.unit_value??'')}"} |
| UI-072 · index.html:99 | input · npr. 01–10/2026 | {"data-effect": "${i}", "data-field": "period", "value": "${esc(x.period\|\|'')}", "placeholder": "npr. 01–10/2026"} |
| UI-073 · index.html:99 | textarea · ${esc(x.evidence\|\|'')} | {"rows": "2", "data-effect": "${i}", "data-field": "evidence"} |
| UI-074 · index.html:99 | button · Ukloni | {"class": "btn secondary", "onclick": "if(confirm('Ukloniti nalaz?')){effects().splice(${i}, 1); save(); render()}"} |
| UI-075 · index.html:129 | button · Nacrt po pravilima | {"class": "btn secondary", "onclick": "makeDraft('${dim}')"} |
| UI-076 · index.html:129 | button · AI nacrt (server) | {"class": "btn secondary", "onclick": "makeAIDraft('${dim}')"} |
| UI-077 · index.html:129 | button · Odobri demo | {"class": "btn", "onclick": "approveReview('${dim}')"} |
| UI-078 · index.html:129 | textarea · ${esc(r.edited)} | {"rows": "9", "data-review": "${dim}", "placeholder": "Kliknite 'Pripremi analitički nacrt'"} |
| UI-079 · index.html:131 | button · + Nova kompanija | {"class": "btn", "onclick": "addCompany()"} |
| UI-080 · index.html:131 | button · Vrati METALPRO simulaciju | {"class": "btn secondary", "onclick": "resetDemo()"} |
| UI-081 · index.html:131 | button · + Nova dijagnostika | {"class": "btn secondary", "onclick": "addDiagnostic()"} |
| UI-082 · index.html:131 | select · ${workspace.companies.map(x=&gt;&#96; ${esc(x.company.name)} &#96;).join('')} | {"id": "companySelect"} |
| UI-083 · index.html:131 | option · ${esc(x.company.name)} | {"value": "${esc(x.id)}", "${x.id": "==c.id?'selected':''}"} |
| UI-084 · index.html:131 | select · ${c.diagnostics.map(x=&gt;&#96; ${esc(x.name)} · ${esc(x.date)} &#96;).join('')} | {"id": "diagnosticSelect"} |
| UI-085 · index.html:131 | option · ${esc(x.name)} · ${esc(x.date)} | {"value": "${esc(x.id)}", "${x.id": "==d.id?'selected':''}"} |
| UI-086 · index.html:131 | button · Otvori | {"class": "btn secondary", "onclick": "chooseDiagnostic('${x.id}')"} |
| UI-087 · index.html:132 | input · generisano polje | {"data-company": "${k}", "value": "${esc(c[k])}"} |
| UI-088 · index.html:133 | button · Otvori modul | {"class": "btn secondary", "onclick": "page='m:${d}'; render()"} |
| UI-089 · index.html:134 | button · ${guidedMode?'Prikaži sve kriterije (brzi unos)':'Vođeni unos, jedno pitanje'} | {"class": "btn secondary", "onclick": "toggleGuided()"} |
| UI-090 · index.html:134 | button · Izvještaj modula | {"class": "btn secondary", "onclick": "page='report'; render()"} |
| UI-091 · index.html:134 | button · 0)?'disabled':''} onclick="guidedMove('${d}',-1)"&gt;← Prethodno | {"class": "btn secondary", "${!(guidedposition[d]": null} |
| UI-092 · index.html:134 | button · =arr.length-1?'disabled':''} onclick="guidedMove('${d}', 1)"&gt;Sljedeće → | {"class": "btn secondary", "${(guidedposition[d]\|\|0)": null} |
| UI-093 · index.html:134 | select · Da Nije primjenjivo (obrazložiti) | {"data-code": "${c.code}", "data-field": "applicable"} |
| UI-094 · index.html:134 | option · Da | {"value": "yes", "${a.applicable!": "='no'?'selected':''}"} |
| UI-095 · index.html:134 | option · Nije primjenjivo (obrazložiti) | {"value": "no", "${a.applicable": "=='no'?'selected':''}"} |
| UI-096 · index.html:134 | select · Nije provjereno U provjeri Potvrđeno Dokaz nedostupan | {"data-code": "${c.code}", "data-field": "proof"} |
| UI-097 · index.html:134 | option · Nije provjereno | {"value": "none", "${!a.proof\|\|a.proof": "=='none'?'selected':''}"} |
| UI-098 · index.html:134 | option · U provjeri | {"value": "review", "${a.proof": "=='review'?'selected':''}"} |
| UI-099 · index.html:134 | option · Potvrđeno | {"value": "confirmed", "${a.proof": "=='confirmed'?'selected':''}"} |
| UI-100 · index.html:134 | option · Dokaz nedostupan | {"value": "missing", "${a.proof": "=='missing'?'selected':''}"} |
| UI-101 · index.html:134 | select · Nepoznato / još nije ocijenjeno ${[0, 1, 2, 3, 4, 5].map(n=&gt;&#96; ${n} &#96;).join('')} | {"data-code": "${c.code}", "data-field": "score"} |
| UI-102 · index.html:134 | option · Nepoznato / još nije ocijenjeno | {"value": ""} |
| UI-103 · index.html:134 | option · ${n} | {"value": "${n}", "${string(a.score)": "==String(n)?'selected':''}"} |
| UI-104 · index.html:134 | input · ${esc(c.kpi)} | {"data-code": "${c.code}", "data-field": "kpi", "value": "${esc(a.kpi)}", "placeholder": "${esc(c.kpi)}"} |
| UI-105 · index.html:134 | textarea · ${esc(a.evidence)} | {"data-code": "${c.code}", "data-field": "evidence", "placeholder": "Obavezno za potvrdu: izvor, referentni period, dokument ili zapis"} |
| UI-106 · index.html:134 | textarea · ${esc(a.na_reason\|\|a.evidence\|\|'')} | {"data-code": "${c.code}", "data-field": "na_reason"} |
| UI-107 · index.html:134 | input · na_approved_by | {"data-code": "${c.code}", "data-field": "na_approved_by", "value": "${esc(a.na_approved_by\|\|'')}"} |
| UI-108 · index.html:134 | textarea · ${esc(a.finding)} | {"data-code": "${c.code}", "data-field": "finding"} |
| UI-109 · index.html:134 | textarea · ${esc(a.financial)} | {"data-code": "${c.code}", "data-field": "financial"} |
| UI-110 · index.html:134 | textarea · ${esc(a.recommendation\|\|'')} | {"data-code": "${c.code}", "data-field": "recommendation"} |
| UI-111 · index.html:138 | button · Kratki pregled | {"class": "btn secondary", "onclick": "openReport('${d}', false)"} |
| UI-112 · index.html:138 | button · Detaljni pregled | {"class": "btn secondary", "onclick": "openReport('${d}', true)"} |
| UI-113 · index.html:138 | button · Word · sažetak | {"class": "btn", "onclick": "exportDOCX('${d}', false)"} |
| UI-114 · index.html:138 | button · Word · detaljno | {"class": "btn", "onclick": "exportDOCX('${d}', true)"} |
| UI-115 · index.html:139 | button · + Dodaj aktivnost | {"class": "btn", "onclick": "state.plan.push({task:'', owner:'', due:'', kpi:'', status:'Nije počelo'}); save(); render()"} |
| UI-116 · index.html:139 | input · ${k} | {"data-plan": "${i}", "data-field": "${k}", "value": "${esc(a[k])}"} |
| UI-117 · index.html:139 | button · Ukloni | {"class": "btn secondary controls", "onclick": "state.plan.splice(${i}, 1); save(); render()"} |
| UI-118 · index.html:140 | button · Izvezi JSON kopiju | {"class": "btn", "onclick": "exportJSON()"} |
| UI-119 · index.html:140 | input · generisano polje | {"type": "file", "accept": ".json, application/json", "style": "display:none", "onchange": "importJSON(this.files[0]); this.value=''"} |
| UI-120 · index.html:140 | button · Obriši lokalne podatke | {"class": "btn secondary", "onclick": "if(confirm('Obrisati sve lokalne podatke?')){localStorage.removeItem(KEY); location.reload()}"} |
| UI-121 · index.html:158 | button · Štampaj / sačuvaj PDF | {"onclick": "print()"} |
| UI-122 · index.html:247 | button · ${integratedAIBusy?'AI analizira...':'Pokreni integrisanu AI analizu'} | {"class": "btn", "onclick": "runIntegratedAI()", "${integratedaibusy?'disabled':''}": null} |
| UI-123 · index.html:248 | button · Kopiraj AI nacrt | {"class": "btn secondary", "onclick": "navigator.clipboard.writeText(integratedAIDraft)"} |
| UI-124 · index.html:250 | textarea · '+esc(integratedAIDraft)+' | {"readonly": null, "style": "min-height: 550 px; white-space:pre-wrap"} |
| UI-125 · index.html:268 | button · ${decisionBusy?'AI priprema odluke...':'Predloži direktorske odluke'} | {"class": "btn", "onclick": "runDecisionIntelligence()", "${decisionbusy?'disabled':''}": null} |
| UI-126 · index.html:269 | button · Kopiraj prijedlog odluka | {"class": "btn secondary", "onclick": "navigator.clipboard.writeText(decisionDraft)"} |
| UI-127 · index.html:271 | textarea · '+esc(decisionDraft)+' | {"readonly": null, "style": "min-height: 550 px; white-space:pre-wrap"} |
| UI-128 · index.html:287 | button · ${v 2Busy?'Analiza u toku…':'Pokreni integrisanu analizu'} | {"class": "btn", "onclick": "runV2()", "${v2 busy?'disabled':''}": null} |
| UI-129 · index.html:287 | button · Stručni pregled | {"class": "btn secondary", "onclick": "page='review'; render()"} |
| UI-130 · index.html:295 | button · Dopuni osnovice i dokaze | {"class": "btn secondary", "onclick": "page='finance'; render()"} |
| UI-131 · index.html:357 | button · Konsultantska provjera i završni izvještaji | {"class": "btn secondary", "onclick": "openDiagnosticReview()"} |
| UI-132 · index.html:357 | button · ${v 3Busy?'Analiza u toku…':'Pokreni kompletnu dijagnostiku'} | {"class": "btn", "onclick": "runV3()", "${v3 busy?'disabled':''}": null} |
| UI-133 · index.html:357 | button · Word · Executive Summary | {"class": "btn secondary", "onclick": "exportV3(false)"} |
| UI-134 · index.html:357 | button · Word · Detaljni izvještaj | {"class": "btn secondary", "onclick": "exportV3(true)"} |
| UI-135 · index.html:357 | button · Pređi na izbor operativnog projekta | {"class": "btn", "onclick": "openV3ProjectCandidates()"} |
| UI-136 · index.html:407 | a · Preuzmi JSON | {"href": "/api/backup", "download": null} |
| UI-137 · index.html:407 | input · mevan-restore-file | {"type": "file", "id": "mevan-restore-file", "accept": ".json, application/json", "style": "max-width: 175 px"} |
| UI-138 · index.html:407 | button · Vrati | {"type": "button", "onclick": "mevanRestoreBackup()"} |
| UI-139 · index.html:143 | a · Dinamička kontrola: ll, 2)],{type:'application/json'}), u=URL.createObjectURL(b), a=document.createElement('a'); a.href=u; a.download='mevan-workspace-backup.json'; a.click(); setTimeout(()=&gt;URL.revokeObjectURL(u), 1000)} | JS createElement; broj instanci zavisi od podataka |
| UI-140 · index.html:229 | a · Dinamička kontrola: const blob=zipStore(entries), url=URL.createObjectURL(blob), a=document.createElement('a'); a.href=url; a.download='MEVAN_'+(dim==='ALL'?'UKUPNO':dim)+'_'+(detailed?'Detaljni':'Sazetak')+'.docx'; a.click(); setTimeout(()=&gt;URL.revokeObjectURL(url), 2000) | JS createElement; broj instanci zavisi od podataka |
| UI-141 · index.html:405 | a · Dinamička kontrola: st blob=zipStore(entries), url=URL.createObjectURL(blob), link=document.createElement('a'); link.href=url; link.download='MEVAN_v 3_4_'+(detailed?'Comprehensive':'Executive')+'_NACRT.docx'; link.click(); setTimeout(()=&gt;URL.revokeObjectURL(url), 3000); | JS createElement; broj instanci zavisi od podataka |


### Definicije iz `projects_ui.html`

| ID / izvor | Tip i oznaka/sadržaj | Ulaz / obrada / uslov |
| --- | --- | --- |
| UI-142 · projects_ui.html:3 | a · ← Dijagnostika | {"href": "/"} |
| UI-143 · projects_ui.html:3 | a · Portfolio dashboard | {"href": "/dashboard-ui"} |
| UI-144 · projects_ui.html:3 | button · Osvježi | {"onclick": "refresh()"} |
| UI-145 · projects_ui.html:3 | summary · Napredno: ručni JSON unos | statički tag ili tag u JS predlošku |
| UI-146 · projects_ui.html:3 | textarea ·  | {"id": "analysisJson", "style": "min-height: 115 px", "placeholder": "{\"ai\":{\"decisions\":[{\"title\":\"...\",\"why\":\"...\"}]}}"} |
| UI-147 · projects_ui.html:3 | button · Prikaži kandidate iz JSON-a | {"onclick": "loadCandidates()"} |
| UI-148 · projects_ui.html:3 | button · Sačuvaj ocjene na server | {"type": "button", "class": "secondary", "onclick": "saveCandidateDraftServer()"} |
| UI-149 · projects_ui.html:3 | button · Učitaj ocjene sa servera | {"type": "button", "class": "secondary", "onclick": "restoreCandidateDraftServer()"} |
| UI-150 · projects_ui.html:3 | button · Prikaži rangiranje C1–C3 | {"type": "button", "id": "showRanking", "class": "secondary", "onclick": "showCandidateRanking()", "disabled": null} |
| UI-151 · projects_ui.html:3 | button · Generiši AI nacrt | {"id": "generatePack", "onclick": "generatePack()", "disabled": null} |
| UI-152 · projects_ui.html:3 | button · Preliminarni nacrt bez AI | {"id": "generateBasic", "class": "secondary", "onclick": "generatePack(true)", "disabled": null} |
| UI-153 · projects_ui.html:3 | input · npr. METALPRO-DEMO | {"id": "newCompany", "placeholder": "npr. METALPRO-DEMO"} |
| UI-154 · projects_ui.html:3 | input · npr. demo-2026 | {"id": "newDiagnostic", "placeholder": "npr. demo-2026"} |
| UI-155 · projects_ui.html:3 | input · Naziv prioritetnog projekta | {"id": "newTitle", "placeholder": "Naziv prioritetnog projekta"} |
| UI-156 · projects_ui.html:3 | textarea ·  | {"id": "newProblem", "placeholder": "Najmanje 10 znakova"} |
| UI-157 · projects_ui.html:3 | button · Kreiraj nacrt | {"onclick": "createDraft()"} |
| UI-158 · projects_ui.html:3 | button · Izvezi Word | {"type": "button", "class": "secondary", "onclick": "downloadReport('docx')"} |
| UI-159 · projects_ui.html:3 | button · Izvezi PDF | {"type": "button", "class": "secondary", "onclick": "downloadReport('pdf')"} |
| UI-160 · projects_ui.html:3 | textarea ·  | {"id": "problem"} |
| UI-161 · projects_ui.html:3 | textarea ·  | {"id": "objective"} |
| UI-162 · projects_ui.html:3 | textarea ·  | {"id": "scope"} |
| UI-163 · projects_ui.html:3 | textarea ·  | {"id": "methodology"} |
| UI-164 · projects_ui.html:3 | textarea ·  | {"id": "assumptions"} |
| UI-165 · projects_ui.html:3 | textarea ·  | {"id": "required_checks"} |
| UI-166 · projects_ui.html:3 | button · + Dodaj aktivnost | {"type": "button", "class": "secondary", "id": "addActivity", "onclick": "addStructured('activities')"} |
| UI-167 · projects_ui.html:3 | button · + Dodaj KPI | {"type": "button", "class": "secondary", "id": "addKpi", "onclick": "addStructured('kpis')"} |
| UI-168 · projects_ui.html:3 | summary · Finansijski efekti — JSON lista (nepotvrđeni) | statički tag ili tag u JS predlošku |
| UI-169 · projects_ui.html:3 | textarea ·  | {"id": "financial_effects", "style": "min-height: 120 px"} |
| UI-170 · projects_ui.html:3 | button · + Dodaj korist u svaki scenarij | {"type": "button", "class": "secondary", "onclick": "addBenefitRow()", "id": "financeAddBenefit"} |
| UI-171 · projects_ui.html:3 | button · Izračunaj | {"type": "button", "onclick": "previewFinance()", "id": "financePreview"} |
| UI-172 · projects_ui.html:3 | button · Sačuvaj scenarije | {"type": "button", "onclick": "saveFinance()", "id": "financeSave"} |
| UI-173 · projects_ui.html:3 | input · baseline_verified | {"style": "width:auto", "type": "checkbox", "id": "baseline_verified"} |
| UI-174 · projects_ui.html:3 | input · targets_approved | {"style": "width:auto", "type": "checkbox", "id": "targets_approved"} |
| UI-175 · projects_ui.html:3 | input · checks_completed | {"style": "width:auto", "type": "checkbox", "id": "checks_completed"} |
| UI-176 · projects_ui.html:3 | button · Sačuvaj nacrt | {"id": "save", "onclick": "save()"} |
| UI-177 · projects_ui.html:3 | button · Odobri fazu validacije | {"id": "validation", "class": "secondary", "onclick": "transition('approve-validation')"} |
| UI-178 · projects_ui.html:3 | button · Odobri implementaciju | {"id": "implementation", "onclick": "transition('approve-implementation')"} |
| UI-179 · projects_ui.html:3 | input · 2026-11 | {"id": "actualPeriod", "placeholder": "2026-11"} |
| UI-180 · projects_ui.html:3 | input · Smanjenje škarta | {"id": "actualName", "placeholder": "Smanjenje škarta"} |
| UI-181 · projects_ui.html:3 | select · Operativna ušteda Kontribucijska marža Izbjegnuti trošak Jednokratni obrtni kapital | {"id": "actualCategory"} |
| UI-182 · projects_ui.html:3 | option · Operativna ušteda | {"value": "operating_saving"} |
| UI-183 · projects_ui.html:3 | option · Kontribucijska marža | {"value": "contribution_margin"} |
| UI-184 · projects_ui.html:3 | option · Izbjegnuti trošak | {"value": "avoided_cost"} |
| UI-185 · projects_ui.html:3 | option · Jednokratni obrtni kapital | {"value": "working_capital_release"} |
| UI-186 · projects_ui.html:3 | input · actualAmount | {"id": "actualAmount", "type": "number", "min": "0", "step": "0.01"} |
| UI-187 · projects_ui.html:3 | input · Dokument / izvještaj / oznaka | {"id": "actualEvidence", "placeholder": "Dokument / izvještaj / oznaka"} |
| UI-188 · projects_ui.html:3 | input · Odgovorna osoba | {"id": "actualOwner", "placeholder": "Odgovorna osoba"} |
| UI-189 · projects_ui.html:3 | textarea ·  | {"id": "actualCalculation"} |
| UI-190 · projects_ui.html:3 | input · actualConfirmed | {"id": "actualConfirmed", "type": "checkbox", "style": "width:auto"} |
| UI-191 · projects_ui.html:3 | input · npr. racun-2026-11-001 | {"id": "actualEvent", "maxlength": "128", "pattern": "[A-Za-z 0-9._:-]{1, 128}", "placeholder": "npr. racun-2026-11-001"} |
| UI-192 · projects_ui.html:3 | button · Evidentiraj efekat | {"type": "button", "id": "actualSubmit", "onclick": "addActual()"} |
| UI-193 · projects_ui.html:3 | input · week | {"type": "week", "id": "week"} |
| UI-194 · projects_ui.html:3 | textarea ·  | {"id": "blockers"} |
| UI-195 · projects_ui.html:3 | textarea ·  | {"id": "decisions"} |
| UI-196 · projects_ui.html:3 | textarea ·  | {"id": "weekNote"} |
| UI-197 · projects_ui.html:3 | button · Sačuvaj sedmični pregled | {"onclick": "addWeek()"} |
| UI-198 · projects_ui.html:8 | input · Dinamička kontrola: createElement('div'), l=document.createElement('label'), input=document.createElement('input'); l.textContent=label; input.value=obj[field]===undefined\|\|obj[field]===null?'':String(obj[field]); input.disabled=!editable; input.addEventListener('input',()=&gt;{obj[field]=input.value}); wrap.append(l, i | JS createElement; broj instanci zavisi od podataka |
| UI-199 · projects_ui.html:8 | button · Dinamička kontrola: nd(l, input); grid.append(wrap)}section.append(grid); const del=document.createElement('button'); del.type='button'; del.className='secondary'; del.textContent='Ukloni'; del.disabled=!editable; del.onclick=()=&gt;{structured[type].splice(index, 1); renderStructured(type)}; section.append(del); root.appen | JS createElement; broj instanci zavisi od podataka |
| UI-200 · projects_ui.html:15 | input · Dinamička kontrola: t.createElement('div'), l=document.createElement('label'), inp=document.createElement('input'); l.textContent=label; inp.type=type; if(type==='number'){inp.min='0'; inp.step='0.01'}inp.value=value??''; inp.disabled=!editable; inp.addEventListener('input',()=&gt;change(inp.value)); wrap.append(l, inp); r | JS createElement; broj instanci zavisi od podataka |
| UI-201 · projects_ui.html:16 | select · Dinamička kontrola: t.createElement('div'), l=document.createElement('label'), sel=document.createElement('select'); l.textContent='Kategorija'; FIN_CATEGORIES.forEach(([value, text])=&gt;{const opt=document.createElement('option'); opt.value=value; opt.textContent=text; sel.append(opt)}); sel.value=b.category; sel.disabl | JS createElement; broj instanci zavisi od podataka |
| UI-202 · projects_ui.html:16 | option · Dinamička kontrola: ategorija'; FIN_CATEGORIES.forEach(([value, text])=&gt;{const opt=document.createElement('option'); opt.value=value; opt.textContent=text; sel.append(opt)}); sel.value=b.category; sel.disabled=!editable; sel.addEventListener('change',()=&gt;b.category=sel.value); selWrap.append(l, sel); g.append(selWrap, fi | JS createElement; broj instanci zavisi od podataka |
| UI-203 · projects_ui.html:16 | button · Dinamička kontrola: a', b.assumption, v=&gt;b.assumption=v)); wrap.append(g); const del=document.createElement('button'); del.type='button'; del.className='secondary'; del.textContent='Ukloni korist'; del.disabled=!editable\|\|s.benefits.length===1; del.onclick=()=&gt;{s.benefits.splice(bi, 1); renderFinance()}; wrap.append(del) | JS createElement; broj instanci zavisi od podataka |
| UI-204 · projects_ui.html:24 | select · Dinamička kontrola: reateElement('label'); l.textContent=label+' (0–5)'; const inp=document.createElement('select'); inp.id='factor_'+c.id+'_'+key; for(const [value, text] of [['','Nije ocijenjeno'],...Array.from({length: 6},(_, i)=&gt;[String(i), String(i)])]){const o=document.createElement('option'); o.value=value; o.te | JS createElement; broj instanci zavisi od podataka |
| UI-205 · projects_ui.html:24 | option · Dinamička kontrola: rray.from({length: 6},(_, i)=&gt;[String(i), String(i)])]){const o=document.createElement('option'); o.value=value; o.textContent=text; inp.append(o)}const why=document.createElement('textarea'); why.rows=2; why.style.minHeight='64 px'; why.id='why_'+c.id+'_'+key; why.placeholder='Objasnite očekivani ut | JS createElement; broj instanci zavisi od podataka |
| UI-206 · projects_ui.html:24 | textarea · Dinamička kontrola: n'); o.value=value; o.textContent=text; inp.append(o)}const why=document.createElement('textarea'); why.rows=2; why.style.minHeight='64 px'; why.id='why_'+c.id+'_'+key; why.placeholder='Objasnite očekivani uticaj, pretpostavke i izvor procjene (najmanje 15 znakova)'; const evidence=document.createE | JS createElement; broj instanci zavisi od podataka |
| UI-207 · projects_ui.html:24 | input · Dinamička kontrola: tavke i izvor procjene (najmanje 15 znakova)'; const evidence=document.createElement('input'); evidence.id='evidence_'+c.id+'_'+key; evidence.placeholder='ID dokaza (opcionalno, odvojeni zarezom)'; const hint=document.createElement('p'); hint.className='muted'; hint.textContent=FACTOR_GUIDANCE[k | JS createElement; broj instanci zavisi od podataka |
| UI-208 · projects_ui.html:54 | button · Dinamička kontrola: '); box.replaceChildren(); for(const p of data.projects){let b=document.createElement('button'); b.className='item'+(p.id===selected?' active':''); b.textContent=p.title+' · '+p.status; b.onclick=()=&gt;openProject(p.id); box.append(b)}if(!data.projects.length){let p=document.createElement('p'); p.c | JS createElement; broj instanci zavisi od podataka |
| UI-209 · projects_ui.html:62 | a · Dinamička kontrola:   const link=document.createElement('a'), url=URL.createObjectURL(await response.blob()); | JS createElement; broj instanci zavisi od podataka |
| UI-210 · projects_ui.html:67 | summary · Dinamička kontrola: eekly_reviews\|\|[]){let d=document.createElement('details'), s=document.createElement('summary'), p=document.createElement('pre'); s.textContent=w.week; p.textContent='Aktivnosti: '+(w.activities\|\|[]).map(a=&gt;(a.title\|\|'Aktivnost')+' — '+(a.status\|\|'bez statusa')).join('; ')+'\nKPI: '+(w.kpi_mea | JS createElement; broj instanci zavisi od podataka |
| UI-211 · projects_ui.html:71 | option · Dinamička kontrola: toku'], ['done','Završeno'], ['blocked','Blokirano']]){const o=document.createElement('option'); o.value=v; o.textContent=t; x.append(o)}x.value=value\|\|'not_started'}else{x.type='text'; x.value=value??''}w.append(x); return {w, x}} | JS createElement; broj instanci zavisi od podataka |


### Definicije iz `server.py`

| ID / izvor | Tip i oznaka/sadržaj | Ulaz / obrada / uslov |
| --- | --- | --- |
| UI-212 · server.py:98 | form · MEVAN Diagnostic Privatni demonstracijski pristup E-mail Lozinka Prijavi se | {"method": "post", "action": "/login"} |
| UI-213 · server.py:98 | input · csrf_token | {"type": "hidden", "name": "csrf_token", "value": "__CSRF_TOKEN__"} |
| UI-214 · server.py:98 | input · email | {"name": "email", "type": "email", "required": null, "autocomplete": "username"} |
| UI-215 · server.py:98 | input · password | {"name": "password", "type": "password", "required": null, "autocomplete": "current-password"} |
| UI-216 · server.py:98 | button · Prijavi se | statički tag ili tag u JS predlošku |
| UI-217 · server.py:117 | a · Pokušaj ponovo | {"href": "/login"} |

## JS funkcije i vezivanja događaja

Statički inventar obuhvata imenovane function i arrow definicije te linije createElement/oninput/onchange/onclick/addEventListener. Jedna linija može deklarisati više kontrola; puna linija i source su u JSON inventaru, radi provjere dinamičke generacije. Imena u tabeli nisu nove specifikacije ili tvrdnja o izvršenom browser pokrivanju svake grane.

| ID | Izvor | Funkcija / interakcija | Vrsta |
| --- | --- | --- | --- |
| JS-001 | dashboard_ui.html:5 | render | funkcija |
| JS-002 | dashboard_ui.html:5 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-003 | dashboard_ui.html:6 | load | funkcija |
| JS-004 | dashboard_ui.html:6 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-005 | diagnostic_review.html:23 | api | funkcija |
| JS-006 | diagnostic_review.html:29 | field | funkcija |
| JS-007 | diagnostic_review.html:30 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-008 | diagnostic_review.html:31 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-009 | diagnostic_review.html:34 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-010 | diagnostic_review.html:36 | listDownloads | funkcija |
| JS-011 | diagnostic_review.html:39 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-012 | diagnostic_review.html:40 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-013 | diagnostic_review.html:42 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-014 | diagnostic_review.html:46 | init | funkcija |
| JS-015 | diagnostic_review.html:78 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-016 | diagnostic_review.html:80 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-017 | diagnostic_review.html:82 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-018 | diagnostic_review.html:85 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-019 | diagnostic_review.html:86 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-020 | diagnostic_review.html:88 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-021 | diagnostic_review.html:96 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-022 | diagnostic_review.html:115 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-023 | diagnostic_review.html:116 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-024 | diagnostic_review.html:117 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-025 | diagnostic_review.html:118 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-026 | diagnostic_review.html:119 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-027 | diagnostic_review.html:120 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-028 | diagnostic_review.html:123 | save | funkcija |
| JS-029 | diagnostic_review.html:142 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-030 | diagnostic_review.html:143 | updateMode | funkcija |
| JS-031 | diagnostic_review.html:150 | updateMissing | funkcija |
| JS-032 | diagnostic_review.html:168 | showStage | funkcija |
| JS-033 | diagnostic_review.html:178 | showProject | funkcija |
| JS-034 | diagnostic_review.html:180 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-035 | diagnostic_review.html:182 | createGuidedProject | funkcija |
| JS-036 | diagnostic_review.html:190 | projectApi | funkcija |
| JS-037 | diagnostic_review.html:209 | seedDemo | funkcija |
| JS-038 | diagnostic_review.html:234 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-039 | index.html:23 | guidedMove | funkcija |
| JS-040 | index.html:24 | toggleGuided | funkcija |
| JS-041 | index.html:31 | crossChecks | funkcija |
| JS-042 | index.html:42 | assessmentQuality | funkcija |
| JS-043 | index.html:48 | qualityPanel | funkcija |
| JS-044 | index.html:52 | scoreHelp | funkcija |
| JS-045 | index.html:53 | criterionWarnings | funkcija |
| JS-046 | index.html:74 | chooseCompany | funkcija |
| JS-047 | index.html:75 | chooseDiagnostic | funkcija |
| JS-048 | index.html:76 | resetDemo | funkcija |
| JS-049 | index.html:77 | addCompany | funkcija |
| JS-050 | index.html:78 | addDiagnostic | funkcija |
| JS-051 | index.html:97 | effects | funkcija |
| JS-052 | index.html:98 | financialTotals | funkcija |
| JS-053 | index.html:99 | financePage | funkcija |
| JS-054 | index.html:103 | draftAnalysis | funkcija |
| JS-055 | index.html:115 | reviewRecord | funkcija |
| JS-056 | index.html:116 | reviewFingerprint | funkcija |
| JS-057 | index.html:117 | makeDraft | funkcija |
| JS-058 | index.html:118 | makeAIDraft | funkcija |
| JS-059 | index.html:128 | approveReview | funkcija |
| JS-060 | index.html:129 | reviewPage | funkcija |
| JS-061 | index.html:130 | render | funkcija |
| JS-062 | index.html:130 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-063 | index.html:141 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-064 | index.html:142 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-065 | index.html:143 | exportJSON | funkcija |
| JS-066 | index.html:143 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-067 | index.html:144 | importJSON | funkcija |
| JS-068 | index.html:158 | openReport | funkcija |
| JS-069 | index.html:162 | crc 32 | funkcija |
| JS-070 | index.html:163 | zipStore | funkcija |
| JS-071 | index.html:179 | exportDOCX | funkcija |
| JS-072 | index.html:229 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-073 | index.html:234 | runIntegratedAI | funkcija |
| JS-074 | index.html:244 | integratedAISection | funkcija |
| JS-075 | index.html:255 | runDecisionIntelligence | funkcija |
| JS-076 | index.html:265 | decisionSection | funkcija |
| JS-077 | index.html:276 | runV2 | funkcija |
| JS-078 | index.html:285 | v 2Page | funkcija |
| JS-079 | index.html:300 | cloudBoot | funkcija |
| JS-080 | index.html:320 | v 31Money | funkcija |
| JS-081 | index.html:321 | v 31FinanceHtml | funkcija |
| JS-082 | index.html:329 | analysisInput | funkcija |
| JS-083 | index.html:332 | analysisSignature | funkcija |
| JS-084 | index.html:335 | openDiagnosticReview | funkcija |
| JS-085 | index.html:344 | runV3 | funkcija |
| JS-086 | index.html:355 | v 3Page | funkcija |
| JS-087 | index.html:366 | openV3ProjectCandidates | funkcija |
| JS-088 | index.html:379 | exportV3 | funkcija |
| JS-089 | index.html:405 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-090 | index.html:408 | mevanRestoreBackup | funkcija |
| JS-091 | projects_ui.html:8 | renderStructured | funkcija |
| JS-092 | projects_ui.html:8 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-093 | projects_ui.html:9 | addStructured | funkcija |
| JS-094 | projects_ui.html:13 | blankBenefit | funkcija |
| JS-095 | projects_ui.html:14 | newFinanceModel | funkcija |
| JS-096 | projects_ui.html:15 | financeField | funkcija |
| JS-097 | projects_ui.html:15 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-098 | projects_ui.html:16 | renderFinance | funkcija |
| JS-099 | projects_ui.html:16 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-100 | projects_ui.html:17 | addBenefitRow | funkcija |
| JS-101 | projects_ui.html:18 | getFinancePayload | funkcija |
| JS-102 | projects_ui.html:19 | renderFinanceResult | funkcija |
| JS-103 | projects_ui.html:19 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-104 | projects_ui.html:20 | loadFinance | funkcija |
| JS-105 | projects_ui.html:21 | previewFinance | funkcija |
| JS-106 | projects_ui.html:22 | saveFinance | funkcija |
| JS-107 | projects_ui.html:24 | loadCandidates | funkcija |
| JS-108 | projects_ui.html:24 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-109 | projects_ui.html:25 | ratingPayload | funkcija |
| JS-110 | projects_ui.html:26 | showCandidateRanking | funkcija |
| JS-111 | projects_ui.html:31 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-112 | projects_ui.html:32 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-113 | projects_ui.html:33 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-114 | projects_ui.html:37 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-115 | projects_ui.html:38 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-116 | projects_ui.html:41 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-117 | projects_ui.html:48 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-118 | projects_ui.html:50 | generatePack | funkcija |
| JS-119 | projects_ui.html:52 | notify | funkcija |
| JS-120 | projects_ui.html:53 | api | funkcija |
| JS-121 | projects_ui.html:54 | refresh | funkcija |
| JS-122 | projects_ui.html:54 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-123 | projects_ui.html:55 | createDraft | funkcija |
| JS-124 | projects_ui.html:56 | downloadReport | funkcija |
| JS-125 | projects_ui.html:62 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-126 | projects_ui.html:67 | openProject | funkcija |
| JS-127 | projects_ui.html:67 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-128 | projects_ui.html:68 | getCharter | funkcija |
| JS-129 | projects_ui.html:69 | save | funkcija |
| JS-130 | projects_ui.html:70 | transition | funkcija |
| JS-131 | projects_ui.html:71 | weeklyField | funkcija |
| JS-132 | projects_ui.html:71 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-133 | projects_ui.html:72 | renderWeeklyForms | funkcija |
| JS-134 | projects_ui.html:72 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-135 | projects_ui.html:73 | weeklyPayload | funkcija |
| JS-136 | projects_ui.html:74 | addWeek | funkcija |
| JS-137 | projects_ui.html:78 | candidateDraftKey | funkcija |
| JS-138 | projects_ui.html:79 | saveCandidateDraft | funkcija |
| JS-139 | projects_ui.html:92 | currentCandidateDraft | funkcija |
| JS-140 | projects_ui.html:102 | candidateServerKey | funkcija |
| JS-141 | projects_ui.html:103 | displaySavedRanking | funkcija |
| JS-142 | projects_ui.html:106 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-143 | projects_ui.html:107 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-144 | projects_ui.html:108 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-145 | projects_ui.html:111 | candidateServerStatus | funkcija |
| JS-146 | projects_ui.html:112 | fetchCandidateDraftServer | funkcija |
| JS-147 | projects_ui.html:120 | saveCandidateDraftServer | funkcija |
| JS-148 | projects_ui.html:139 | restoreCandidateDraftServer | funkcija |
| JS-149 | projects_ui.html:162 | restoreCandidateDraft | funkcija |
| JS-150 | projects_ui.html:180 | installCandidateDraftAutosave | funkcija |
| JS-151 | projects_ui.html:182 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-152 | projects_ui.html:184 | receiveDiagnosticTransfer | funkcija |
| JS-153 | projects_ui.html:215 | loadActuals | funkcija |
| JS-154 | projects_ui.html:215 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-155 | projects_ui.html:217 | addActual | funkcija |
| JS-156 | qa_word_reports.js:3 | extractMainScript | funkcija |
| JS-157 | qa_word_reports.js:5 | exportDOCX | funkcija |
| JS-158 | qa_word_reports.js:12 | generate | funkcija |
| JS-159 | qa_word_reports.js:18 | dinamička kontrola/vezivanje događaja | dinamički JS |
| JS-160 | dashboard_ui.html:4 | el | imenovana streličasta funkcija |
| JS-161 | diagnostic_review.html:20 | get | imenovana streličasta funkcija |
| JS-162 | diagnostic_review.html:196 | due | imenovana streličasta funkcija |
| JS-163 | index.html:9 | makeAssessment | imenovana streličasta funkcija |
| JS-164 | index.html:10 | makeCompany | imenovana streličasta funkcija |
| JS-165 | index.html:56 | activeCompany | imenovana streličasta funkcija |
| JS-166 | index.html:57 | activeDiagnostic | imenovana streličasta funkcija |
| JS-167 | index.html:59 | syncState | imenovana streličasta funkcija |
| JS-168 | index.html:62 | save | imenovana streličasta funkcija |
| JS-169 | index.html:80 | get | imenovana streličasta funkcija |
| JS-170 | index.html:81 | valid | imenovana streličasta funkcija |
| JS-171 | index.html:82 | applicable | imenovana streličasta funkcija |
| JS-172 | index.html:83 | naValid | imenovana streličasta funkcija |
| JS-173 | index.html:84 | summary | imenovana streličasta funkcija |
| JS-174 | index.html:85 | fmt | imenovana streličasta funkcija |
| JS-175 | index.html:86 | indexText | imenovana streličasta funkcija |
| JS-176 | index.html:87 | moduleName | imenovana streličasta funkcija |
| JS-177 | index.html:88 | moduleNav | imenovana streličasta funkcija |
| JS-178 | index.html:161 | utf 8 | imenovana streličasta funkcija |
| JS-179 | index.html:165 | u 16 | imenovana streličasta funkcija |
| JS-180 | index.html:166 | header | imenovana streličasta funkcija |
| JS-181 | index.html:178 | xmlEsc | imenovana streličasta funkcija |
| JS-182 | index.html:186 | add | imenovana streličasta funkcija |
| JS-183 | index.html:187 | page | imenovana streličasta funkcija |
| JS-184 | index.html:188 | cell | imenovana streličasta funkcija |
| JS-185 | index.html:189 | table | imenovana streličasta funkcija |
| JS-186 | index.html:190 | status | imenovana streličasta funkcija |
| JS-187 | index.html:226 | sty | imenovana streličasta funkcija |
| JS-188 | index.html:382 | add | imenovana streličasta funkcija |
| JS-189 | index.html:383 | page | imenovana streličasta funkcija |
| JS-190 | index.html:384 | cell | imenovana streličasta funkcija |
| JS-191 | index.html:385 | table | imenovana streličasta funkcija |
| JS-192 | index.html:386 | list | imenovana streličasta funkcija |
| JS-193 | index.html:402 | sty | imenovana streličasta funkcija |
| JS-194 | projects_ui.html:51 | el | imenovana streličasta funkcija |
| JS-195 | qa_word_reports.js:18 | element | imenovana streličasta funkcija |
