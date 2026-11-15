# Spécifications des composants

## Sources et limites

La recon Android s’appuie sur des captures d’écran publiques de la fiche
Google Play, et non sur une installation de l’application. Elle confirme
directement une liste de chansons renseignée, un écran de karaoké avec paroles,
un éditeur d’effets vocaux et un écran consacré aux duos. Les autres écrans et
états du catalogue et de l’éditeur restent inconnus. Les présentes
spécifications décrivent un système visuel accessible et réutilisable pour le
nouveau produit; elles ne reprennent ni l’identité visuelle de StarMaker ni ses
éléments de marque.

Utiliser les jetons définis dans `tokens.css`. Prévoir des libellés textuels et
des commandes accessibles. N’utiliser que des illustrations originales et
des morceaux disposant de licences indépendantes. Toutes les commandes doivent
conserver un focus clavier très visible et des zones tactiles confortables.

## Bouton

- **Variantes :** action principale, secondaire, discrète/lien, destructive.
- **Tailles :** petit, 36 px; moyen, 44 px; grand, 48 px. Minimum de 44 × 44 px
  pour les boutons sans libellé et les commandes tactiles.
- **États :** par défaut, survolé, activé, focus-visible (contour `focus` de
  2 px avec décalage visible), désactivé, en attente.
- **Jetons :** action sémantique, texte de contraste sur l’action,
  `radius-md`, `font-size-sm`.
- **Accessibilité :** élément natif `<button>`; signaler l’opération en cours
  avec `aria-busy="true"` et un statut annoncé poliment, tout en conservant le
  nom accessible. Ne jamais utiliser uniquement la couleur pour indiquer une
  action destructive ou en attente. Un bouton désactivé ne déclenche aucune
  mutation ni soumission.
- **Utilisation :** S01 à S06.

## Bouton avec icône

- **Variantes :** lecture/aperçu, duo, fermeture/annulation, menu secondaire.
- **Tailles :** minimum 44 × 44 px; réserver 40 × 40 px aux contextes
  exclusivement pointeur ou ordinateur.
- **États :** par défaut, survolé, activé, focus-visible, désactivé.
- **Jetons :** `interactive`, `surface-raised`, `border`, `radius-pill`,
  `focus`.
- **Accessibilité :** bouton natif doté d’un nom accessible, traduit et adapté
  à l’action. Masquer le glyphe décoratif aux technologies d’assistance. Ne pas
  utiliser d’emoji ni d’icônes StarMaker copiées dans la version finale.
- **Utilisation :** S01, S02, S03, S05, S06.

## Champ de recherche

- **Variantes :** recherche dans le catalogue; filtre de langue facultatif.
- **Tailles :** pleine largeur sur petit écran; largeur limitée sur grand
  écran; hauteur minimale de 44 px.
- **États :** inactif, sélectionné, contient une requête, chargement, aucun
  résultat, erreur, désactivé.
- **Jetons :** `surface`, `text`, `text-muted`, `border-input`, `focus`,
  `radius-md`.
- **Accessibilité :** libellé visible en permanence; un texte indicatif ne
  suffit pas. Dans le catalogue, placer le champ dans un repère de recherche.
  Donner au bouton d’effacement un nom annoncé par le lecteur d’écran.
  Annoncer calmement le nombre de résultats et ne pas annoncer chaque résultat
  à chaque frappe.
- **Utilisation :** S01.

## Ligne de chanson et entrée du catalogue

- **Variantes :** ligne de liste avec titre, artiste et langue; tuile compacte
  dans une grille adaptative.
- **Tailles :** zone tactile d’au moins 56 px de haut. L’image de pochette est
  décorative, sauf si elle apporte une information absente du texte.
- **États :** renseignée, sélectionnée, indisponible pour raisons de droits,
  squelette de chargement, filtrée/sans résultat, erreur du catalogue,
  métadonnées en cache hors ligne. Les états de droits et hors ligne sont des
  recommandations pour le nouveau produit, pas des observations de la recon.
- **Jetons :** `surface`, `surface-raised`, `border`, `text`, `text-muted`,
  `radius-md`, `shadow-card`.
- **Accessibilité :** présenter le titre, l’artiste et la langue dans l’ordre
  de lecture. Donner des noms explicites aux commandes d’aperçu et de chant.
  Ne pas exprimer la disponibilité des droits uniquement par la transparence.
- **Utilisation :** S01.

## Lecteur de karaoké et paroles synchronisées

- **Variantes :** capture verticale, prise audio seule; lecteur complet ou
  compact.
- **États :** chargement, prêt, lecture, pause, application en arrière-plan,
  interrompu, titre indisponible, erreur de lecture, permission refusée,
  animations réduites. La galerie publique montre les paroles actives. Les
  autres états sont à vérifier sur des appareils Android.
- **Jetons :** `bg`, `surface`, `text`, `text-muted`, `accent`,
  `surface-raised`. Distinguer visuellement les paroles actives des paroles
  inactives synchronisées.
- **Accessibilité :** proposer des commandes de lecture accessibles sans
  geste; annoncer l’état de lecture et d’enregistrement sans lire sans cesse
  chaque parole; prévoir un mode paroles compatible avec le lecteur d’écran
  et expliquer clairement la demande d’accès au microphone. Ne pas démarrer
  un enregistrement à l’ouverture de l’écran.
- **Utilisation :** S02.

## Commande d’enregistrement

- **Variantes :** démarrer, mettre en pause/reprendre, terminer, confirmer la
  suppression.
- **États :** inactif, demande de permission, prêt, enregistrement, pause,
  permission refusée, microphone occupé, interruption, stockage saturé, erreur
  de capture.
- **Jetons :** `accent-action`, `on-accent-action`, `danger`, `surface`,
  `border`, `focus`.
- **Accessibilité :** fournir un nom d’action et un état explicites. Afficher
  la durée écoulée et en limiter les annonces vocales. Libeller séparément les
  commandes terminer et supprimer. Ne demander l’autorisation du microphone
  qu’après une action explicite de la personne.
- **Utilisation :** S02.

## Préréglages et réglages audio

- **Variantes :** préréglages clairement nommés, réglage de la hauteur,
  réduction du bruit, décalage du repère d’enregistrement; limiter les valeurs
  acceptées par l’API.
- **États :** prise originale chargée, modifications non enregistrées,
  traitement en cours, aperçu traité, enregistrement réussi, erreur de
  traitement, confirmation des changements non enregistrés, commande
  indisponible.
- **Jetons :** `surface`, `surface-raised`, `border-input`, `text`,
  `text-muted`, `accent-action`, `focus`.
- **Accessibilité :** donner un nom textuel aux effets. Les curseurs annoncent
  leur nom, leur plage et leur valeur. Permettre les réglages numériques ou
  par paliers, sans glissement obligatoire. Prévoir une vraie commande
  d’aperçu avec états lecture et arrêt.
- **Utilisation :** S03. Les plages des curseurs et l’enregistrement des
  réglages sont des propositions, pas des mesures de l’application de
  référence.

## Aperçu et partage d’une performance

- **Variantes :** aperçu privé d’un brouillon, publication avec consentement
  explicite, lien de partage avec expiration, révocation du lien.
- **États :** brouillon, traitement en cours, privé/prêt, publié, expiré,
  révoqué, erreur d’enregistrement/envoi, nouvelle tentative hors ligne.
- **Jetons :** `surface`, `surface-raised`, `border`, `text`, `text-muted`,
  `accent-action`, `danger`.
- **Accessibilité :** demander une action explicite et compréhensible avant
  toute publication. Indiquer clairement la visibilité publique et l’expiration
  du lien. Permettre la révocation au clavier et au toucher. Annoncer la
  confirmation du partage comme un statut.
- **Utilisation :** S05.

## Invitation à un duo et prise d’un participant

- **Variantes :** créer un duo pour une personne inscrite, recevoir une
  invitation, accepter, refuser, consulter l’état de sa propre prise, écouter
  le mix asynchrone finalisé.
- **États :** en attente, acceptée, enregistrement, envoyée, refusée, expirée,
  titre indisponible, erreur de traitement.
- **Jetons :** `surface`, `surface-raised`, `border`, `text`, `text-muted`,
  `accent`, `accent-action`, `focus`.
- **Accessibilité :** annoncer le rôle et l’état de l’invitation sans révéler
  la performance privée d’un participant aux autres personnes. Prévoir une
  action explicite pour quitter ou annuler. Afficher aux personnes autorisées
  la version du titre et de son repère de synchronisation.
- **Utilisation :** S06.
- **Périmètre :** la première version propose des duos asynchrones entre
  personnes déjà inscrites. Les collaborations avec des artistes et le chant
  synchronisé en direct nécessitent des droits et une validation technique
  distincts.

## Fenêtre modale et confirmation

- **Variantes :** confirmer une suppression, consentir à une publication,
  inviter à un duo, expliquer une permission ponctuelle.
- **Tailles :** largeur limitée à la colonne de contenu; sur mobile, panneau
  pleine largeur avec marges adaptées à la zone de sécurité de l’écran.
- **États :** ouverte, validation, envoi, erreur, fermée.
- **Jetons :** `surface`, `text`, `text-muted`, `border`, `shadow-pop`,
  `radius-lg`, `focus`.
- **Accessibilité :** nommer la fenêtre, placer le focus de façon intentionnelle
  à son ouverture et le garder à l’intérieur pendant la navigation au clavier.
  Documenter le comportement d’Échap et de fermeture, rendre l’arrière-plan
  inerte, puis rétablir le focus sur la commande qui l’a ouverte.
- **Utilisation :** S02, S03, S05, S06.

## Notification éphémère et message d’état

- **Variantes :** enregistrement réussi, traitement en cours, erreur pouvant
  être résolue.
- **États :** annonce polie, alerte prioritaire uniquement en cas de blocage
  urgent, fermeture au clavier ou au toucher.
- **Jetons :** `surface-raised`, `text`, `border`, `success`, `danger`,
  `warning`.
- **Accessibilité :** choisir le rôle de région dynamique adapté; ne pas
  déplacer le focus; laisser le message affiché assez longtemps pour être lu.
  Si la récupération demande une action, conserver aussi une erreur visible
  et persistante.
- **Utilisation :** S01 à S06.

## Navigation adaptative et mise en page

- **Grand écran :** navigation fixe, en-tête de page et contenu centré, limité
  à 1 440 px; ces valeurs ne sont pas des observations de l’application de
  référence.
- **Tablette :** navigation rétractable, contenu réparti en une ou deux
  colonnes selon l’espace disponible.
- **Téléphone :** interface pleine largeur, commandes faciles d’accès et
  respect des zones de sécurité; ne pas transformer l’écran d’enregistrement
  en grille de bureau dense.
- **Points de rupture :** 620, 800 et 1 100 px sont les seuils initiaux de la
  mise en page web, pas des exigences liées à des modèles de téléphone. Tester
  sur les appareils visés et avec un texte agrandi.
- **Accessibilité :** utiliser `aria-current="page"` pour la destination
  active; nommer et ordonner correctement les repères; garder le focus visible
  après la navigation et conserver une hiérarchie logique des titres.

## Limites de conception et de vérification

Aucun logo StarMaker, visuel de la boutique, image sous licence, fichier de
police, pochette, icône ni texte promotionnel copié n’est inclus dans ce
système de conception. Les couleurs sombres sémantiques et leurs valeurs
appartiennent au nouveau produit; elles ne prétendent pas reproduire une palette
mesurée dans l’application. La fiche publique ne permet pas d’observer les
états vides, les permissions, les erreurs, les chargements ni le comportement
adaptatif. Vérifier ces états dans le prototype au lieu de les présenter comme
des observations de référence.
