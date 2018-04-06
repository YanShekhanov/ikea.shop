
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
                    to_paste.append('<li><a href="/shop/product_detail/product=' + data.products[product].article_number + '">"' + data.products[product].title + ' ' + data.products[product].article_number +  '</a></li>')
                };
                to_paste.show();
            },
            error:console.log('error')
        })
    }

