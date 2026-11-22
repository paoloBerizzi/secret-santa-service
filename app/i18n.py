from fastapi import Request

LANGUAGE_COOKIE = 'santa_language'
LANGUAGES = ('it', 'en')

ITALIAN = {
    'New exchange': 'Nuovo scambio',
    'Create event': 'Crea evento',
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