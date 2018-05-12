    var castom_tags = ['<%', '%>'];

//*loader
    $(window).ready(function () {
        $('#load').fadeOut(600);
    });

    function loader_hide(){
        $('#load').fadeOut(600);
    };

    function loader_show() {
        $('#load').fadeIn(300);
    };

    //*скрыть объекты
    function hide_tags(tags_list){
        for (itter=0; itter<tags_list.length; itter++){
            $(tags_list[itter]).hide();
        };
    };

    //*удалить объекты
    function remove_tags(tags_list){
        for (itter=0; itter<tags_list.length; itter++){
            $(tags_list[itter]).remove();
        };
    }

    //наведение на карточку и появление иконки открытия дополнительных иображений
    function hover_product_card() {
        $('.card').hover(function () {
            $(this).find('.get-all-images').fadeIn(300);
        }, function () {
            $(this).find('.get-all-images').fadeOut(300);
        });
    };

    function search(searched_text, token, template) {
        $.ajax({
            url:'/search/',
            type:'json',
            method:'POST',
            data:{
                'csrfmiddlewaretoken': token,
                'searched_text': searched_text,
            },
            success:function (data) {
                console.log(data.products.length);
                to_paste = $('#searched_query');
                to_paste.find('li').remove();
                to_paste.hide();
                Mustache.tags = ['<%', '%>'];
                for (product=0; product<data.products.length; product++){
                    rend_data = {image_url:data.products[product].product_image,
                                 product_title:data.products[product].product_title,
                                 product_article_number:data.products[product].product_article_number,
                                 product_price:data.products[product].product_price,
                                };
                    var rend_html = Mustache.render(template, rend_data);
                    console.log(rend_data);
                    to_paste.prepend(rend_html);
                }
                to_paste.show();
            },
            error:function () {
                console.log('error')
            },
        })
    };


    //*сортировка*//
    function get_sort(sort_by, unique_identificator , token, template){
        $.ajax({
            url: '/getSortQuery/',
            method: 'POST',
            data:{
                'csrfmiddlewaretoken':token,
                'sort_by':sort_by,
                'unique_identificator':unique_identificator,
            },
            success:function (data) {
                for (one_product=0; one_product<data.data.length; one_product++){
                    generate_one_product_card(data.data[one_product], template); //*генерируем карточки продуктов
                };
                hide_tags(tags_list); //*скрываем стандартно скрытые блоки
                hover_product_card(); //*при наведении появляется иконка просмотра изображений
                $('#product-cards').fadeIn(1800, loader_hide()); //*делаем видимыми карточки продуктов
            },
            error:function () {
                console.log('error')
            },
        })
    };

    //*генерация карточки*//
        function generate_one_product_card(product_query, template) {
            Mustache.tags = ['<%', '%>'];
            rendered_data = {
                product_article_number:product_query.article_number,
                product_title:product_query.title,
                product_price:product_query.price,
                product_dimensions:product_query.dimensions,
                image_url:product_query.image,
                unique_identificator:product_query.unique_identificator,
            };
            var rendered_html = Mustache.render(template, rendered_data);
            console.log(rendered_html);
            $('#product-cards').append(rendered_html);
        }


    function check_availability(article_number, callback){
            $.ajax({
                url:'/checkAvailability/',
                method:'POST',
                data:{
                    'csrfmiddlewaretoken':token,
                    'article_number':article_number
                },
                success: function (data) {
                    $to_paste = $('#product_available');
                    if (data.availability){
                        callback(data.availability);
                        return data.availability;
                    } else if (data.successMessage){
                        callback(data.successMessage);
                        return data.successMessage;
                    } else if (data.errorMessage){
                        callback(data.errorMessage);
                        return data.errorMessage;
                    }
                },
                error: function () {
                    return ('функция недоступна, попробуйте позже')
                }
            });
        }

    function ajax_add_to_basket(token, product_article_number, product_count, callback){
            $.ajax({
                url: '/basket/add_to_basket/',
                method:'POST',
                data:{
                    'csrfmiddlewaretoken':token,
                    'product_article':product_article_number,
                    'count':product_count,
                },
                success: function (data) {
                    callback(data);
                    refresh_basket_price(token);
                },
                error: function () {
                    console.log('error');
                }
            })
    }

    function refresh_basket_price(token){
            $.ajax({
                url: '/basket/refresh_basket_price/',
                method: 'POST',
                data: {
                    'csrfmiddlewaretoken':token
                },
                success:function (data) {
                    console.log(data);
                    $('.amount-circle').html(data.order.product_count);
                    $('#price').html(data.order.order_price);
                },
                error:function (data) {
                    console.log(data);
                },
            })

    }

    //ajax загрузка изображений артикула
        $('body').on('click', '.get-all-images', function (){
            var token = $('input[name="csrfmiddlewaretoken"]').val();
            var unique_identificator = $(this).data('unique_identificator');
            console.log(unique_identificator);

            $.ajax({
                url: "{% url 'get_all_product_images' %}",
                method: 'post',
                data: {
                    'csrfmiddlewaretoken':token,
                    'unique_identificator':unique_identificator
                },
                success: function (data) {
                    $block_to_paste_images = $('.img-block');
                    $block_to_paste_images.slideDown(function () {
                        $('.big-image').append('<img class="big-img-item" src="' + data.images[0] + '" alt="#">');
                        for (i=0; i<data.images.length; i++) {
                            $('.mini-img-list').append('<img class="mini-img" src="' + data.images[i] + '" alt="#">');
                    };

                    });
                }

            });

            //клик на маленькое изображение и загрузка большого
            $('.img-block').on('click', '.mini-img', function() {
                var img=$(this);
                $('.big-img-item').attr('src', img.attr('src'));
            });

            //закрытие блока с загруженными изображениями
            $('#close_images_icon').click(function () {
                console.log('ok');
                $('.img-block').find('img').remove();
                $('.img-block').slideUp();
            });
        });




