
    function hide_tags(tags_list){
        for (itter=0; itter<tags_list.length; itter++){
            $(tags_list[itter]).hide();
        };
    };

    //наведение на карточку и появление иконки открытия дополнительных иображений
    function hover_product_card() {
        $('.card').hover(function () {
            $(this).find('.get-all-images').show();
        }, function () {
            $(this).find('.get-all-images').hide();
        });
    };

    function search(searched_text, token) {
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
                    to_paste.append('<li><a href="/shop/product_detail/product=' + data.products[product].article_number + '">' + data.products[product].title + ' ' + data.products[product].article_number +  '</a></li>')
                };
                to_paste.show();
            },
            error:console.log('error')
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
                hide_tags(['.card']);
                for (one_product=0; one_product<data.data.length; one_product++){
                    $one_product_card = $('#product-cards').append($('#hidden-template').html());
                    generate_one_product_card(data.data[one_product]);
                };
                hide_tags(tags_list);
                hover_product_card();
            },
            error:console.log('error')
        })
    };

    //*генерация карточки*//
        function generate_one_product_card(product_query) {
            $this_card = $('.card').last();
            $this_card.attr('id', product_query.article_number);
            $this_card.find('.card-title').text(product_query.title);
            $this_card.find('.card-text').text(product_query.description);
            $this_card.find('.card-price').text(product_query.price + ' PLN');
            $this_card.find('.get-all-images').attr('data-unique_identificator', product_query.unique_identificator);
            $this_card.find('.btn-info').attr('onclick', 'window.location.href=' + "'/shop/product_detail/product=" + product_query.article_number + "'");
            $this_card.find('.productImage').attr('src', product_query.image);
        }




