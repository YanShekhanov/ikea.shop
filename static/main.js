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
            url:'/shop/search/',
            type:'json',
            method:'POST',
            data:{
                'csrfmiddlewaretoken': token,
                'searched_text': searched_text,
            },
            success:function (data) {
                to_paste = $('#searched_query');
                to_paste.find('li').remove();
                to_paste.hide();
                for (product=0; product<data.products.length; product++){
                    render_template = {'image_url':'', 'product_title':data.products[product].title, 'article_number':data.products[product].article_number};
                    var html = Mustache.render(template, render_template, castom_tags);
                    console.log(html);
                };
                to_paste.show();
            },
            error:function () {
                console.log('error')
            },
        })
    };


    //*сортировка*//
    function get_sort(sort_by, unique_identificator , token){
        $.ajax({
            url: '/shop/getSortQuery/',
            method: 'POST',
            data:{
                'csrfmiddlewaretoken':token,
                'sort_by':sort_by,
                'unique_identificator':unique_identificator,
            },
            success:function (data) {
                for (one_product=0; one_product<data.data.length; one_product++){
                    $one_product_card = $('#product-cards').append($('#product-card').html());
                    generate_one_product_card(data.data[one_product]); //*генерируем карточки продуктов
                };
                hide_tags(tags_list); //*скрываем стандартно скрытые блоки
                hover_product_card(); //*при наведении появляется иконка просмотра изображений
                $('#product-cards').fadeIn(1800); //*делаем видимыми карточки продуктов
                loader_hide(); //*убераем лоадер
            },
            error:function () {
                console.log('error')
            },
        })
    };

    //*генерация карточки*//
        function generate_one_product_card(product_query) {
            $this_card = $('.card').last();
            $this_card.attr('id', product_query.article_number);
            $this_card.find('.card-title').text(product_query.title);
            $this_card.find('.card-title').attr('href', '/shop/product_detail/product=' + product_query.article_number);
            $this_card.find('.card-text').text(product_query.description);
            $this_card.find('.card-price').text(product_query.price + ' PLN');
            $this_card.find('.get-all-images').attr('data-unique_identificator', product_query.unique_identificator);
            $this_card.find('.btn-info').attr('onclick', 'window.location.href=' + "'/shop/product_detail/product=" + product_query.article_number + "'");
            $this_card.find('.productImage').attr('src', product_query.image);
            $this_card.find('.ind-code').text(product_query.article_number);
        }


    function check_availability(article_number){
            var token = $('input[name="csrfmiddlewaretoken"]').val();
            $.ajax({
                url:'{% url "checkAvailability" %}',
                method:'POST',
                data:{
                    'csrfmiddlewaretoken':token,
                    'article_number':article_number,
                },
                success: function (data) {
                    if (data.availability){

                    }
                    console.log(data.availability);
                },
                error: function () {
                    console.log('error')
                },
            })
    }




