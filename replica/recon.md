# Recon : StarMaker: Sing Karaoke Songs (Android)

Périmètre : parcours karaoké principal sur Android : choisir un morceau, chanter et modifier un enregistrement, puis le partager ou lancer un duo.
Public : grand public, pour le produit karaoké de la personne à l’origine du projet.
Date : 2026-11-15

## Sources

| # | source | URL | notes |
| --- | --- | --- | --- |
| 1 | Fiche de l’application sur Google Play | https://play.google.com/store/apps/details?id=com.starmakerinteractive.starmaker | Fiche officielle de StarMaker par SKYWORK AI PTE. LTD.; description des fonctions, cinq captures publiques de l’application, contact de l’assistance, date de mise à jour et résumé des informations sur la sécurité des données. Les images de la galerie ont été consultées comme références et ne sont pas incluses dans ce dépôt. |
| 2 | Site officiel StarMaker (français) | https://www.starmakerstudios.com/fr | Lien indiqué sur la fiche Google Play. Présentation promotionnelle et liens de téléchargement Android/iOS; les affirmations concernant les utilisatrices, utilisateurs et le produit n’ont pas été vérifiées indépendamment. |
| 3 | Informations Google Play sur la sécurité des données | https://play.google.com/store/apps/datasafety?id=com.starmakerinteractive.starmaker | Lien de la fiche de l’application. Informations déclarées par le développeur concernant la collecte et le partage, le chiffrement en transit et les demandes de suppression. |

La fiche consultée ne fournissait de lien ni vers un centre d’aide public distinct, ni vers des tarifs détaillés, un journal des modifications ou de la documentation d’API. Elle indiquait une adresse d’assistance, mais aucun article d’aide n’a pu être consulté dans les sources examinées. L’application n’a pas été installée et aucune session n’a été ouverte; les transitions, permissions et états autres que le parcours principal restent donc à vérifier.

## Parcours principal

Choisir un titre de karaoké, chanter sur l’accompagnement et les paroles, retoucher la prise vocale, puis enregistrer ou partager la performance ou participer à un duo.

## Écrans

| ID | écran | itinéraire / accès | objectif | composants principaux | états observés |
| --- | --- | --- | --- | --- | --- |
| S01 | Catalogue de chansons | Application Android; choisir un titre. La capture de la fiche Google Play montre une liste renseignée; aucun lien profond public. | Choisir un titre dans un catalogue local et international. | Lignes de titres et vignettes de pochettes; le texte de la capture est trop petit pour identifier d’autres commandes. | Catalogue renseigné visible dans la capture 2 de la fiche. États vide, chargement et erreur non observés. |
| S02 | Performance karaoké | Choisir un titre et lancer une session. Les captures 1 et 4 de la galerie montrent des écrans de performance; la transition exacte n’est pas montrée. | Chanter sur un accompagnement avec paroles à l’écran et indication de justesse. | Aperçu vidéo du chanteur, paroles, commandes d’enregistrement et d’accompagnement, indication de justesse. | Performance avec paroles et chanteur visible; détection de justesse décrite dans la fiche. Permissions, pause, erreur et états vides non observés. |
| S03 | Éditeur vocal | Après ou pendant une performance; déduit de la capture 3 de la galerie. | Régler les effets de la prise vocale. | Préréglages nommés, curseurs de réglage, commandes d’aperçu ou d’action. | Écran de sélection d’effets et de réglages visible. États enregistrer/annuler et erreurs non observés. |
| S04 | Éditeur de clips vidéo | À partir d’un enregistrement; aucun itinéraire distinct n’est montré. Cette fonction est décrite sur la fiche Google Play. | Créer un clip avec un modèle de paroles et appliquer des filtres vidéo. | Modèles vidéo, incrustation des paroles, filtres vidéo. | Fonction décrite dans la fiche; écran ni état particulier vérifié visuellement. |
| S05 | Aperçu et partage d’un enregistrement | Après l’enregistrement; itinéraire et mise en page non montrés. | Écouter ou télécharger un enregistrement et partager une performance. | Aperçu, commandes d’enregistrement et de partage déduits des fonctions d’enregistrement, de téléversement et de téléchargement décrites dans la fiche. | Actions décrites dans la fiche; aucun écran ni état particulier vérifié visuellement. |
| S06 | Performance en duo | Choisir un duo avec un ami ou une artiste; l’accès exact n’est pas montré. La capture 5 de la galerie met en avant les duos. | Chanter avec une autre personne ou sur l’enregistrement d’un artiste. | Images de plusieurs chanteurs ou avatars et commande de duo, d’après la galerie et la description de la fonction. | Le duo est présenté comme une fonction, mais ni invitation, ni synchronisation, ni indisponibilité d’un partenaire n’ont été observées. |

## Parcours

```
F01 Choisir une chanson et partager une performance karaoké
    S01 -> S02 -> S03 -> S04 ou S05
    nombre de pressions dans le parcours idéal : impossible à déterminer à partir des sources publiques consultées
    cas limites à vérifier dans l’application : aucun titre trouvé, permission microphone ou caméra refusée,
          latence audio, retouche abandonnée et échec d’enregistrement ou de partage

F02 Lancer un duo
    S01 -> S06 -> S02 -> S03 -> S05
    nombre de pressions dans le parcours idéal : impossible à déterminer; la source confirme la fonction,
          mais pas ses étapes
    cas limites à vérifier dans l’application : partenaire indisponible, synchronisation des prises du duo
          et interruption ou échec du téléversement
```

Il s’agit de parcours indicatifs fondés sur des éléments de preuve, et non d’un suivi vérifié de chaque écran. Aucune session connectée n’a été ouverte, aucun paywall n’a été consulté.

## Composants

| composant | variantes | états | écrans |
| --- | --- | --- | --- |
| Ligne de chanson | pochette et informations du titre | liste renseignée observée; autres états non observés | S01 |
| Lecteur karaoké et paroles | accompagnement avec paroles synchronisées | performance active observée; chargement, pause et erreur non observés | S02 |
| Commandes d’enregistrement | enregistrement et lecture de la prise vocale | performance visible; permissions et échecs d’enregistrement non observés | S02, S05 |
| Commandes d’effets audio | préréglages nommés et curseurs | éditeur visible; valeurs par défaut et sélection non documentées | S03 |
| Commandes de modèles et filtres vidéo | modèles de paroles et filtres vidéo | fonctions décrites; états des composants non observés | S04 |
| Accès au duo | duo entre amis ou avec un artiste | duo présenté comme une fonction; disponibilité et invitation non observées | S06 |
| Commandes d’enregistrement et de partage | écouter, télécharger, publier ou partager | actions décrites; écrans de résultat et d’erreur non montrés | S05 |

## Modèle de données déduit

```
User  id, display_name, profile_media
      éléments de preuve : la source 1 décrit la communauté, les duos entre amis et les enregistrements mis en ligne
      confiance : moyenne; champs et parcours du compte non visibles

Song  id, title, artist, language, backing_track_ref, lyric_timing_ref
      éléments de preuve : la source 1 décrit un catalogue local et international, l’accompagnement et les paroles défilantes
      confiance : moyenne; schéma exact et accès au catalogue inconnus

Performance  id, user_id, song_id, vocal_recording_ref, created_at, publication_state
             éléments de preuve : la source 1 décrit l’enregistrement, les retouches, le téléversement, le téléchargement et l’écoute
             confiance : moyenne; noms des champs et processus de publication déduits

AudioMix  performance_id, effect_preset, pitch_adjustment, noise_reduction, latency_setting
          éléments de preuve : la source 1 décrit des préréglages et des réglages de justesse, de bruit et de latence
          confiance : moyenne; commandes et persistance inconnues

VideoClip  id, performance_id, template_id, filter_id, lyric_overlay
           éléments de preuve : la source 1 décrit des clips vidéo, des modèles de paroles et des filtres vidéo
           confiance : moyenne; existence d’un objet clip distinct et champs déduits

Duet  id, song_id, participant_ids, recording_refs
      éléments de preuve : la source 1 décrit les duos avec des amis ou des artistes
      confiance : moyenne; synchronisation, propriété et modèle relationnel inconnus
```

Relations : `User 1-n Performance`; `Song 1-n Performance`; `Performance 1-1 AudioMix` est une hypothèse de travail; `Performance 0-n VideoClip`; `Duet` référence un morceau et plusieurs personnes ou enregistrements. Ces relations restent à confirmer dans l’application.

## Matrice fonctionnelle

Voir `features.csv`. Obligatoires : 6; souhaitables : 3; facultatives : 4, dont 2 à exclure; exclues : 2.

## Hors périmètre (éléments non reproductibles ou à ne pas copier)

- Le catalogue musical sous licence de StarMaker, ses accompagnements, paroles, masters, enregistrements d’artistes et autres médias protégés. Seul le parcours fonctionnel peut être recréé; les contenus doivent être originaux ou autorisés par des licences distinctes.
- La communauté StarMaker, ses comptes, ses enregistrements, son graphe social et les relations avec ses créateurs. Ces éléments du produit d’origine ne sont pas transférables.
- Les parcours propres au Web et à iOS, puisque la recon demandée porte sur l’application Android.
- Les salons en direct, les Familles, les cadeaux et les interactions communautaires plus larges sont des pistes d’évolution possibles; ils ne sont pas décrits dans cette recon du parcours principal.
- Les achats, les abonnements et la tarification : la fiche indique des achats intégrés, mais leurs offres et leurs prix n’ont pas été recherchés.

## Estimation de taille

6 écrans, 2 parcours, 6 entités. Principales difficultés : accès aux licences du catalogue, capture audio en temps réel et synchronisation des paroles, traitement audio et latence, montage/téléversement vidéo, synchronisation des duos. Taille : L pour un parcours principal prêt à l’usage avec droits médias et infrastructure disponibles; XL pour une réalisation entièrement nouvelle si les licences et la plateforme de médias temps réel ne sont pas déjà en place.
