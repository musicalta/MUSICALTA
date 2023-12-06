$(document).ready(function(){

    function hidePaymentOption() {
        // Check payment option and get Monetico multi payments for hide
        if ($("div").hasClass("o_payment_option_card") == true){
            $(".o_payment_option_card").find("input").each(function() {
                if ($(this).attr('data-provider') == "monetico_multi") {
                    $(this).closest('.o_payment_option_card').hide();
                }
            });
        }
    }

    // Get amount order and monetico minimal amount (for multi payment)
    if ($("form").hasClass("o_payment_form") == true){
        $("form").each(function(index) {
            if(typeof($(this).attr('data-amount')) !== "undefined"){
                var amount_order = $(this).attr('data-amount');
                // Compare the amounts
                var amount_total = parseInt(amount_order);
                var monetico_minimum_amount = parseInt($("#monetico_minimum_amount").val());
                if (amount_total < monetico_minimum_amount) {
                    // Calling the function to hide multi payment option Monetico
                    hidePaymentOption();
                }
            }
        });
    }
});

