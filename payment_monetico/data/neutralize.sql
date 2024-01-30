-- disable monetico payment provider
UPDATE payment_provider
   SET monetico_key = NULL,
       monetico_version = NULL,
       monetico_TPE = NULL,
       monetico_societe = NULL,
       monetico_url_retour_ok = NULL,
       monetico_url_retour_err = NULL;
