import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Configuração da API do Gemini
try:
    import google.generativeai as genai
    GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        model = None
except Exception as e:
    print(f"Aviso ao carregar biblioteca Gemini: {e}")
    model = None

ARQUIVO_DADOS = 'editais_conhecidos.json'
ARQUIVO_MARKDOWN = 'novos_editais.md'
EMAIL_DESTINATARIO = "vitoriacampioniedu@gmail.com"

# Lista com as 97 universidades italianas
SITES_UNIVERSIDADES = {
    "publicas": {
        "Sapienza Università di Roma": "https://www.uniroma1.it/it/notizia/corsi-di-studio-ammissioni-2026-2027",
        "Università di Bologna (Unibo)": "https://bandi.unibo.it/",
        "Università degli Studi di Milano (UniMi)": "https://www.unimi.it/it/studiare/frequentare-un-corso-di-laurea/iscriversi/iscriversi-un-corso-di-laurea",
        "Università degli Studi di Padova (Unipd)": "https://www.unipd.it/avvisi-ammissione-corsi",
        "Università di Pisa (Unipi)": "https://www.unipi.it/index.php/iscrizioni-e-segreterie",
        "Università degli Studi di Firenze (UniFi)": "https://www.unifi.it/it/studiare/ammissioni-e-iscrizioni",
        "Università degli Studi di Napoli Federico II": "https://www.unina.it/didattica/opportunita-laureati/bandi-di-ammissione",
        "Università degli Studi di Torino (UniTo)": "https://www.unito.it/didattica/immatricolazioni-e-iscrizioni",
        "Università Ca' Foscari Venezia": "https://www.unive.it/web/it/10052/ammissione-e-immatricolazione",
        "Università degli Studi di Genova (UniGe)": "https://unige.it/iscrizioni",
        "Università degli Studi di Pavia (UniPv)": "https://unipv.it/it/didattica/iscriversi-un-corso-di-laurea/ammissione-corsi",
        "Università degli Studi di Trento (UniTrento)": "https://www.unitn.it/servizi/239/ammissioni",
        "Università degli Studi di Bari Aldo Moro (UniBa)": "https://www.uniba.it/it/studenti/segreterie-studenti/procedure-iscrizione",
        "Università degli Studi di Palermo (UniPa)": "https://www.unipa.it/target/futuristudenti/",
        "Università degli Studi di Catania (UniAct)": "https://www.unict.it/it/didattica/bandi-di-ammissione",
        "Università degli Studi di Perugia (UniPg)": "https://www.unipg.it/didattica/accesso-corsi-numero-programmato",
        "Università degli Studi di Siena (UniSi)": "https://www.unisi.it/didattica/iscrizioni-e-immatricolazioni",
        "Università degli Studi di Verona (UniVr)": "https://www.univr.it/it/iscrizioni",
        "Università degli Studi di Brescia (UniBs)": "https://www.unibs.it/it/didattica/iscriversi",
        "Università degli Studi di Bergamo (UniBg)": "https://www.unibg.it/servizi/iscriversi",
        "Università degli Studi Roma Tre": "https://www.uniroma3.it/prospettive/iscrizioni/",
        "Università degli Studi di Roma 'Tor Vergata'": "https://web.uniroma2.it/it/percorso/offerta_formativa",
        "Università degli Studi della Campania Luigi Vanvitelli": "https://www.unicampania.it/index.php/didattica/bandi-di-ammissione",
        "Università degli Studi del Salento (UniSalento)": "https://www.unisalento.it/bandi-di-concorso",
        "Università degli Studi di Messina (UniMe)": "https://www.unime.it/it/iscriversi",
        "Università degli Studi di Trieste (UniTs)": "https://www.units.it/futuri-studenti/come-iscriversi",
        "Università degli Studi di Parma (UniPr)": "https://www.unipr.it/iscrizioni",
        "Università degli Studi di Modena e Reggio Emilia (Unimore)": "https://www.unimore.it/bandi.html",
        "Università degli Studi di Ferrara (UniFe)": "https://www.unife.it/it/iscriviti",
        "Università degli Studi di Udine (UniUd)": "https://www.uniud.it/it/didattica/iscrizioni",
        "Università degli Studi di Salerno (UniSa)": "https://www.unisa.it/didattica/immatricolazioni/bandi",
        "Università degli Studi di Cagliari (UniCa)": "https://www.unica.it/unica/it/futuri_studenti.page",
        "Università degli Studi di Sassari (UniSs)": "https://www.uniss.it/didattica/offerta-formativa",
        "Università degli Studi dell'Aquila (Univaq)": "https://www.univaq.it/section.php?id=1587",
        'Università degli Studi "G. d\'Annunzio" Chieti-Pescara': "https://www.unich.it/didattica/iscrizioni",
        "Università degli Studi di Urbino Carlo Bo (UniUrb)": "https://www.uniurb.it/iscrizioni",
        "Università degli Studi della Tuscia (Unitus)": "https://www.unitus.it/it/unitus/iscrizioni",
        "Università degli Studi di Macerata (UniMc)": "https://www.unimc.it/it/iscrizione-e-gestione-carriera",
        "Università degli Studi del Molise (Unimol)": "https://www.unimol.it/didattica/immatricolazioni/",
        "Università degli Studi della Basilicata (Unibas)": "https://portale.unibas.it/site/home/didattica/iscrizioni.html",
        "Università degli Studi del Sannio (Unisannio)": "https://www.unisannio.it/it/didattica/iscriversi",
        "Università Magna Græcia di Catanzaro (UMG)": "https://web.unicz.it/it/page/bandi-di-concorso-per-studenti",
        "Università Politecnica delle Marche (Univpm)": "https://www.univpm.it/Entra/Ingresso_all_Universita",
        "Università del Piemonte Orientale (UPO)": "https://www.uniupo.it/it/tutti-i-bandi",
        "Politecnico di Milano (Polimi)": "https://www.polimi.it/futuri-studenti/test-e-ammissione",
        "Politecnico di Torino (PoliTo)": "https://www.polito.it/didattica/iscriversi-studiare-laurearsi/iscriversi",
        "Politecnico di Bari (PoliBa)": "https://www.poliba.it/it/didattica/iscrizioni",
        "Università Iuav di Venezia": "https://www.iuav.it/Didattica1/AMMISSIONI/",
        "Scuola Normale Superiore di Pisa": "https://www.sns.it/it/ammissione",
        "Scuola Superiore Sant'Anna di Pisa": "https://www.santannapisa.it/it/ammissione-e-formazione",
        "Scuola IMT Alti Studi Lucca": "https://www.imtlucca.it/it/phd/admission",
        "SISSA - Trieste": "https://www.sissa.it/phd-courses",
        "IUSS Pavia": "https://www.iusspavia.it/it/formazione/concorso-di-ammissione"
    },
    "privadas": {
        "Università Bocconi (Milão)": "https://www.unibocconi.it/ammissioni",
        "LUISS Guido Carli (Roma)": "https://www.luiss.it/ammissione",
        "Università Cattolica del Sacro Cuore": "https://www.unicatt.it/ammissione/iscrizione/iscrizione-a-laurea-triennale-e-a-ciclo-unico.html",
        "Università Vita-Salute San Raffaele (Milão)": "https://www.unisr.it/servizi/ammissioni",
        "Humanitas University (Milão)": "https://www.hunimed.eu/it/ammissioni/",
        "Università Campus Bio-Medico di Roma": "https://www.unicampus.it/it/info/bandi-di-concorso",
        "UniCamillus (Roma)": "https://www.unicamillus.org/it/bandi-e-ammissioni/",
        "IULM (Milão)": "https://www.iulm.it/it/iscrizioni-ammissioni",
        "LIUC - Università Carlo Cattaneo": "https://www.liuc.it/ammissione/",
        "LUM Giuseppe Degennaro (Casamassima)": "https://www.lum.it/ammissioni/",
        "Libera Università Maria Ss. Assunta (LUMSA)": "https://www.lumsa.it/didattica_ammissione",
        "Freie Universität Bozen / Libera Università di Bolzano": "https://www.unibz.it/it/applicants/",
        "Università degli Studi di Enna Kore": "https://unikore.it/index.php/it/bandi-ammissione",
        "Università Europea di Roma (UER)": "https://www.universitaeuropeadiroma.it/ammissioni/",
        "Università Campus Link (Roma)": "https://www2.unilink.it/test-ammissione.asp",
        "Università delle Scienze Gastronomiche (Pollenzo)": "https://www.unisg.it/ammissioni/",
        "NABA - Nuova Accademia di Belle Arti": "https://www.naba.it/it/ammissioni",
        "Istituto Marangoni": "https://www.istitutomarangoni.com/it/ammissioni",
        "IED - Istituto Europeo di Design": "https://www.ied.it/ammissioni"
    },
    "telematicas": {
        "Università Niccolò Cusano (Unicusano)": "https://www.unicusano.it/iscrizione",
        "Università Pegaso": "https://www.unipegaso.it/iscrizioni",
        "Unitelma Sapienza": "https://www.unitelmasapienza.it/iscriviti/",
        "Università Mercatorum": "https://www.unimercatorum.it/iscrizioni",
        "Università San Raffaele Roma (Telemática)": "https://www.uniroma5.it/iscrizioni",
        "Università Giustino Fortunato": "https://www.unifortunato.eu/iscrizioni/",
        "Università eCampus": "https://www.uniecampus.it/iscrizione/",
        "Università Marconi (Unimarconi)": "https://www.unimarconi.it/iscrizioni/",
        "Università IUL": "https://www.iuline.it/iscrizioni/",
        "Università Leonardo da Vinci (Unidav)": "https://www.unidav.it/iscrizioni"
    }
}

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def resumir_com_gemini(url_edital, titulo):
    if not model:
        return "Resumo de IA indisponível (chave GEMINI_API_KEY não configurada ou erro no módulo)."
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url_edital, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        texto_pagina = soup.get_text(separator=' ', strip=True)[:4000]
        
        prompt = f"""
        Você é um assistente especialista em admissões universitárias italianas.
        Analise o texto abaixo extraído da página do edital "{titulo}" ({url_edital}).
        
        Faça um resumo bem conciso em Português com os seguintes tópicos em marcadores:
        - 🎓 Cursos/Graus mencionados
        - 📅 Prazos principais (início e fim de inscrições)
        - 📜 Requisitos (idioma, documentos, exames)
        - 💡 Destaques/Observações importantes
        
        Texto da página:
        {texto_pagina}
        """
        
        resposta = model.generate_content(prompt)
        return resposta.text.strip()
    except Exception as e:
        return f"Não foi possível resumir automaticamente: {e}"

def atualizar_markdown(novos_editais):
    conteudo_novo = "# 🇮🇹 Relatório Diário de Editais (Resumo Gemini IA)\n\n"
    
    for universidade, links in novos_editais.items():
        conteudo_novo += f"## 🏫 {universidade}\n\n"
        for item in links:
            conteudo_novo += f"### 📄 [{item['titulo']}]({item['url']})\n\n"
            conteudo_novo += f"**Resumo Gerado por IA:**\n\n{item.get('resumo', 'Sem resumo disponível.')}\n\n"
            conteudo_novo += "---\n\n"

    if os.path.exists(ARQUIVO_MARKDOWN):
        with open(ARQUIVO_MARKDOWN, 'r', encoding='utf-8') as f:
            conteudo_antigo = f.read()
    else:
        conteudo_antigo = ""

    with open(ARQUIVO_MARKDOWN, 'w', encoding='utf-8') as f:
        f.write(conteudo_novo + "\n" + conteudo_antigo)

def enviar_email(novos_editais):
    remetente = os.environ.get('EMAIL_REMETENTE')
    senha_app = os.environ.get('SENHA_APP_GMAIL')

    if not remetente or not senha_app:
        print("Aviso: Credenciais de e-mail não configuradas.")
        return

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = EMAIL_DESTINATARIO
    msg['Subject'] = "🤖 Resumo Diário de IA: Novos Editais Encontrados!"

    corpo = "Olá, Vitória!\n\nO seu monitor encontrou novos editais e a IA do Gemini gerou os seguintes resumos:\n\n"
    for universidade, links in novos_editais.items():
        corpo += f"=== {universidade} ===\n"
        for item in links:
            corpo += f"\n📌 {item['titulo']}\nLink: {item['url']}\n\n"
            corpo += f"RESUMO DA IA:\n{item.get('resumo', 'Sem resumo.')}\n"
            corpo += "-"*40 + "\n"

    corpo += "\n\nVocê também pode copiar estes links e adicionar no seu Gemini Notebook:\nhttps://gemini.google.com/notebook/d52b210c-7939-418f-a725-e86113d0a1a5"

    msg.attach(MIMEText(corpo, 'plain', 'utf-8'))

    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login(remetente, senha_app)
        servidor.sendmail(remetente, EMAIL_DESTINATARIO, msg.as_string())
        servidor.quit()
        print("E-mail com resumo enviado com sucesso!")
    except Exception as e:
        print(f"Falha ao enviar e-mail: {e}")

def monitorar():
    editais_salvos = carregar_dados()
    novidades_por_universidade = {}
    termos_busca = ['bando', 'ammissione', 'concorso', 'iscrizion', 'call']
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for categoria, universidades in SITES_UNIVERSIDADES.items():
        for universidade, url in universidades.items():
            print(f"[{categoria.upper()}] Verificando: {universidade}...")
            if universidade not in editais_salvos:
                editais_salvos[universidade] = []

            try:
                resposta = requests.get(url, headers=headers, timeout=15)
                if resposta.status_code != 200:
                    continue

                soup = BeautifulSoup(resposta.text, 'html.parser')
                links = soup.find_all('a', href=True)

                for link in links:
                    texto = link.get_text().strip().lower()
                    href = link['href']

                    if any(termo in texto for termo in termos_busca) or any(termo in href.lower() for termo in termos_busca):
                        link_completo = urljoin(url, href)

                        if link_completo not in editais_salvos[universidade]:
                            editais_salvos[universidade].append(link_completo)
                            
                            titulo_edital = link.get_text().strip() or "Edital de Ammissione"
                            print(f" -> Novo edital encontrado! Solicitando resumo ao Gemini...")
                            resumo_ia = resumir_com_gemini(link_completo, titulo_edital)
                            
                            if universidade not in novidades_por_universidade:
                                novidades_por_universidade[universidade] = []
                            
                            novidades_por_universidade[universidade].append({
                                'titulo': titulo_edital,
                                'url': link_completo,
                                'resumo': resumo_ia
                            })

            except Exception as e:
                print(f"Erro ao checar {universidade}: {e}")

    if novidades_por_universidade:
        salvar_dados(editais_salvos)
        atualizar_markdown(novidades_por_universidade)
        enviar_email(novidades_por_universidade)
    else:
        print("Nenhum edital novo encontrado.")

if __name__ == "__main__":
    monitorar()
