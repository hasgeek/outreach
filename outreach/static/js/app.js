/*!
 * Start Bootstrap - Agnecy Bootstrap Theme (http://startbootstrap.com)
 * Code licensed under the Apache License v2.0.
 * For details, see http://www.apache.org/licenses/LICENSE-2.0.
 */

// jQuery for page scrolling feature - requires jQuery Easing plugin
$(function() {
    $('a.page-scroll').bind('click', function(event) {
        var $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: $($anchor.attr('href')).offset().top
        }, 1500, 'easeInOutExpo');
        event.preventDefault();
    });
    var header = document.querySelector( '.st-navbar-default' );
    $(window).scroll(function(){
        if(scrollY>=0 && scrollY<=30) {
            $('.st-navbar-default').animate({
                marginTop: 30-scrollY+'px'
            },0, function(){})
        }
        else if(scrollY>30) {
            $('.st-navbar-default').animate({
                marginTop: '0px'
            },0, function(){})
        }
    });
});

// Highlight the top nav as scrolling occurs
$('body').scrollspy({
    target: '.st-navbar-fixed-top'
})

// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
    $('.navbar-toggle:visible').click();
});