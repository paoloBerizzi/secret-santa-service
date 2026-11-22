from fastapi import Request

LANGUAGE_COOKIE = 'santa_language'
LANGUAGES = ('it', 'en')

ITALIAN = {
    'New exchange': 'Nuovo scambio',
    'Create event': 'Crea evento',
    'How to use': 'Come funziona',
    'For organizers': 'Per gli organizzatori',
    'For participants': 'Per i partecipanti',
    'Keep links private': 'Mantieni privati i link',
    'Secret Santa helps you organize a gift exchange without accounts. Each participant gives one gift and receives one gift, and nobody draws themselves.':
        'Secret Santa ti aiuta a organizzare uno scambio di regali senza account. Ogni partecipante fa e riceve un regalo, e nessuno estrae se stesso.',
    'Choose a title, icon, gift budget, currency, and exchange date. Add notes if needed. Enable no reciprocal pairs if two people must not draw each other.':
        'Scegli titolo, icona, budget per il regalo, valuta e data dello scambio. Aggiungi eventuali note. Attiva Escludi gli scambi reciproci se due persone non devono estrarsi a vicenda.',
    'Save the private organizer link immediately. It is your access to the dashboard: there is no login or recovery if you lose it. Anyone with this link can manage the event.':
        "Salva subito il link privato dell'organizzatore. Serve per accedere al pannello: non ci sono login o recupero se lo perdi. Chiunque abbia questo link può gestire l'evento.",
    'Add 2 to 32 people. You can enter their gift ideas and edit or remove participants while the event is a draft.':
        "Aggiungi da 2 a 32 persone. Puoi inserire le loro idee regalo e modificare o rimuovere i partecipanti finché l'evento è in bozza.",
    'Optionally create groups for households or couples, add their members, and enable no intra-group draws. Individual exclusions prevent a specific giver from drawing a specific recipient; they do not automatically apply in reverse.':
        "Puoi creare gruppi per famiglie o coppie, aggiungere i membri e attivare Escludi scambi nel gruppo. Le esclusioni individuali impediscono a una persona di estrarne un'altra specifica; non valgono automaticamente anche nel senso opposto.",
    'This checks whether a complete draw is possible with the saved rules. The result appears below the button and is also checked when the dashboard loads. If nothing changed, clicking again may show the same result. This does not save assignments or activate links. If the rules prevent a draw or the check cannot finish, adjust a restriction and try again.':
        "Verifica se è possibile un'estrazione completa con le regole salvate. Il risultato appare sotto il pulsante e la verifica viene eseguita anche quando si apre il pannello. Se nulla è cambiato, un nuovo clic può mostrare lo stesso risultato. Non salva abbinamenti e non attiva i link. Se le regole impediscono l'estrazione o la verifica non termina, modifica una restrizione e riprova.",
    'Create the assignments once the rules allow a draw. The dashboard does not display all pairings.':
        "Crea gli abbinamenti quando le regole consentono l'estrazione. Il pannello non mostra tutti gli abbinamenti.",
    'Activate the private participant links, then copy each link and send it only to that person. The service does not send emails or messages automatically. Event settings, participants, and rules can no longer be changed, but wishlists remain editable.':
        "Attiva i link privati dei partecipanti, poi copia ogni link e invialo solo alla persona interessata. Il servizio non invia email o messaggi automaticamente. Non sarà più possibile modificare impostazioni, partecipanti e regole, ma le liste dei desideri restano modificabili.",
    'Open the private link your organizer sent you to see your recipient, the budget, the exchange date, and their gift ideas. You cannot see who drew you.':
        "Apri il link privato inviato dall'organizzatore per vedere il destinatario del tuo regalo, il budget, la data dello scambio e le sue idee regalo. Non puoi vedere chi ti ha estratto.",
    'Use Your wishlist to enter your own gift ideas, then save them. Return to the same link to update them; the person giving to you sees your latest saved wishlist. Participant links are available only after the organizer locks the draw. Before that, ask the organizer to enter your ideas.':
        "Usa La tua lista dei desideri per inserire le tue idee regalo e salvarle. Torna allo stesso link per aggiornarle: chi ti farà il regalo vedrà l'ultima lista salvata. I link dei partecipanti sono disponibili solo dopo il blocco dell'estrazione. Prima, chiedi all'organizzatore di inserire le tue idee.",
    'Anyone with a participant link can see that assignment and edit that participant’s wishlist. Do not share your organizer or participant link publicly.':
        "Chiunque abbia il link di un partecipante può vedere il suo abbinamento e modificare la sua lista dei desideri. Non condividere pubblicamente il link dell'organizzatore o dei partecipanti.",
    'To change a draw, the organizer must confirm Reset draw. This deletes the assignments and invalidates old participant links. Run and lock a new draw, then send the new links. Resetting cannot make someone forget a recipient they already saw. If your link stops working, contact your organizer.':
        "Per cambiare un'estrazione, l'organizzatore deve confermare Annulla l'estrazione. Questo elimina gli abbinamenti e disattiva i vecchi link dei partecipanti. Avvia e blocca una nuova estrazione, poi invia i nuovi link. Annullare non può far dimenticare un destinatario già visto. Se il tuo link non funziona più, contatta l'organizzatore.",
    'THE FAMILY EXCHANGE': 'LO SCAMBIO IN FAMIGLIA',
    'Language': 'Lingua',
    'Change language': 'Cambia lingua',
    'Event title': "Titolo dell'evento",
    'Event icon': "Icona dell'evento",
    'Fox': 'Volpe', 'Snowman': 'Pupazzo di neve', 'Santa': 'Babbo Natale',
    'Reindeer': 'Renna', 'Star': 'Stella', 'Bell': 'Campanella',
    'Select a valid event icon.': "Seleziona un'icona valida per l'evento.",
    'Gift budget': 'Budget per il regalo',
    'Currency': 'Valuta',
    'Exchange date': 'Data dello scambio',
    'Event notes': "Note sull'evento",
    'No reciprocal pairs': 'Escludi gli scambi reciproci',
    'Select participant': 'Seleziona un partecipante',
    'Organizer': 'Organizzatore',
    'Copy organizer link': 'Copia il link organizzatore',
    'Draw': 'Estrazione',
    'Check rules': 'Verifica le regole',
    'Run draw': "Avvia l'estrazione",
    'Lock and enable links': 'Blocca e attiva i link',
    'Discard the draw and revoke its links': "Elimina l'estrazione e disattiva i link",
    'Reset draw': "Annulla l'estrazione",
    'Event details': "Dettagli dell'evento",
    'Save settings': 'Salva impostazioni',
    'Participants': 'Partecipanti',
    'Name': 'Nome',
    'Wishlist': 'Lista dei desideri',
    'Save participant': 'Salva partecipante',
    'Remove participant': 'Rimuovi partecipante',
    'Private link': 'Link privato',
    'Copy link': 'Copia link',
    'Add participant': 'Aggiungi partecipante',
    'Subgroups': 'Sottogruppi',
    'No intra-group draws': 'Escludi scambi nel gruppo',
    'Group name': 'Nome del gruppo',
    'Save subgroup': 'Salva sottogruppo',
    'Remove {name}': 'Rimuovi {name}',
    'Remove': 'Rimuovi',
    'Member': 'Membro',
    'Add member': 'Aggiungi membro',
    'Remove subgroup': 'Rimuovi sottogruppo',
    'No subgroups': 'Nessun sottogruppo',
    'Add subgroup': 'Aggiungi sottogruppo',
    'Directed exclusions': 'Esclusioni individuali',
    'cannot draw': 'non può estrarre',
    'No directed exclusions': 'Nessuna esclusione individuale',
    'Giver': 'Chi regala',
    'Excluded recipient': 'Destinatario escluso',
    'Add exclusion': 'Aggiungi esclusione',
    'A valid draw is possible.': "È possibile effettuare un'estrazione valida.",
    'Private Reveal': 'Rivelazione privata',
    'Welcome, {name}!': 'Ciao, {name}!',
    "You're giving to": 'Il tuo regalo è per',
    "{name}'s wishlist": 'Lista dei desideri di {name}',
    'No wishlist yet.': 'Nessun desiderio ancora.',
    'Your wishlist': 'La tua lista dei desideri',
    'Gift ideas': 'Idee regalo',
    'Enter gift ideas you would like to receive this year.': 'Inserisci qui le idee regalo che vorresti ricevere quest’anno.',
    'Save wishlist': 'Salva lista dei desideri',
    'draft': 'Bozza', 'drawn': 'Estratto', 'locked': 'Bloccato',
    'Copied': 'Copiato', 'Could not copy': 'Impossibile copiare',
    'Use 2 to {limit} participants.': 'Inserisci da 2 a {limit} partecipanti.',
    '{name}: members outnumber available recipients outside the subgroup.':
        '{name}: i membri sono più numerosi dei destinatari disponibili fuori dal sottogruppo.',
    '{name} has no valid recipients.': '{name} non ha destinatari disponibili.',
    '{name} has no possible givers.': 'Nessuno può fare un regalo a {name}.',
    'Could not verify within the search limit. Relax a rule and try again.':
        'Non è stato possibile completare la verifica. Modifica una regola e riprova.',
    'The combined rules prevent a complete draw. Try relaxing an exclusion or allowing reciprocal pairs.':
        'Le regole impediscono un’estrazione completa. Modifica un’esclusione o consenti gli scambi reciproci.',
    'Link not found.': 'Link non trovato.',
    'Item not found.': 'Elemento non trovato.',
    'Membership not found.': 'Appartenenza al gruppo non trovata.',
    'The event changed or is not editable. Reload or reset the draw first.':
        "L'evento è cambiato o non è modificabile. Ricarica la pagina o annulla prima l'estrazione.",
    'Reset the existing draw first.': "Annulla prima l'estrazione esistente.",
    'The event changed during validation. Reload and check again.':
        "L'evento è cambiato durante la verifica. Ricarica la pagina e riprova.",
    'That name, membership, or exclusion already exists.':
        'Questo nome, appartenenza o esclusione esiste già.',
    'Confirm that the existing draw and all links should be discarded.':
        "Conferma l'eliminazione dell'estrazione e di tutti i link.",
    'An event can have at most {limit} participants.': 'Un evento può avere al massimo {limit} partecipanti.',
    'Self-draws are already excluded.': 'Non è possibile estrarre se stessi.',
    'Reload the page and submit the form again.': 'Ricarica la pagina e invia di nuovo il modulo.',
    'Select a participant.': 'Seleziona un partecipante.',
    'Enter a nonnegative budget with up to two decimals and select a currency.':
        'Inserisci un budget non negativo con al massimo due decimali e seleziona una valuta.',
    'Enter a valid exchange date.': 'Inserisci una data di scambio valida.',
    'The request was not valid.': 'La richiesta non è valida.',
    'Check the {field} field (limit: {limit} characters).':
        'Controlla il campo {field} (massimo {limit} caratteri).',
    'title': 'titolo', 'budget': 'budget', 'currency': 'valuta', 'exchange_date': 'data dello scambio',
    'notes': 'note', 'name': 'nome', 'wishlist': 'lista dei desideri',
    'participant_id': 'partecipante', 'giver_id': 'chi regala', 'receiver_id': 'destinatario',
}


def language(request: Request) -> str:
    value = request.cookies.get(LANGUAGE_COOKIE, 'it')
    return value if value in LANGUAGES else 'it'


def translate(locale: str, message: str, **values: object) -> str:
    translation = ITALIAN.get(message, message) if locale == 'it' else message
    return translation.format(**values) if values else translation