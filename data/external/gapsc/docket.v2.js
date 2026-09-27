
function getQueryVariable(variable)
{
       var query = window.location.search.substring(1);
       var vars = query.split("&");
       for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
       }
       return(false);
}

let docketRequest = {
    docketId: getQueryVariable('docketId'),
    pageSize: 50,
    sortDirection: 'DESC',
    sortColumn : 'Filed',
    searchText: $('#searchText').val()

}

$(function(){
    $('.search-pagination').hide();
    console.log("main function");

    var matchMediaQuery = window.matchMedia('(max-width: 640px)');

    if(matchMediaQuery != null )
    {
        if(matchMediaQuery.matches)
        {
            LoadDocumentsByDocketId(docketRequest, false, true);
        }
        else{
            LoadDocumentsByDocketId(docketRequest, true, false);
        }

        matchMediaQuery.onchange = function(e) {
            if (e.matches) {
              /* the viewport is 640 pixels wide or less */
              LoadDocumentsByDocketId(docketRequest, false, true);
          
            } else {
              /* the viewport is more than than 640 pixels wide */
              LoadDocumentsByDocketId(docketRequest, true, false);
            }
        }
    }
    else{
        LoadDocumentsByDocketId(docketRequest, true, false);
    }

    SortColOnClick();
    PageSizeOnChange();
    SearchTextOnKeyUp();
    SearchTextClearOnClick();

    $('#pageSize').val('50');

    attachSearchResultEvents();
});



function attachSearchResultEvents() {
    $('.subscription-link').click(function() {
        var entityId = $(this).attr('data-entityId');
        var hasSubcription  = $(this).attr('data-subscription');
        var subscription = {
            userSubscriptions: [
            {
                "title": $('#dockTitle').val(),
                "starsEntityId": "1",
                "starsEntityName": "Docket",
                "entityId": entityId,
                "hasSubscribed": hasSubcription,
                "userId": "0"
            }
        ]};
        $.post('/account-dashboard/service-api/?accountAction=manage-subscriptions', subscription)
            .done(function(data) {
                location.reload()
                
            });
    });
}



function LoadDocumentsByDocketId(docketRequest, showPageNumbers, showNavigator) {
    if(docketRequest != null) {

        $('.search-pagination').hide();
        $('#documentsBody').find('tr:gt(0)').empty();
        $('#documentsBody').find('tr:first').removeClass('hide');
        $('#documentsBody > tr:first > td').text('Loading results...');
        
        var pagingContainer = $('.search-pagination');
        pagingContainer.pagination({
            dataSource: '/search/service-facts-docket/' 
                + '?docketId=' + docketRequest.docketId
                + '&sortDirection=' + docketRequest.sortDirection
                + '&sortColumn=' + docketRequest.sortColumn 
                + '&searchText=' + docketRequest.searchText
                + '&pageSize=' + docketRequest.pageSize, 
            locator: 'resultsItems',
            showLastOnEllipsisShow: true,
            prevText: "&#9664; &nbsp; Previous",
            nextText: "Next &nbsp; &#9654;",
            ellipsisText: "&#8230",
            formatNavigator: '<%= currentPage %> / <%= totalPage %>.',
            showPageNumbers: showPageNumbers,
            showNavigator: showNavigator,
            totalNumberLocator: function(response) {
                return response.resultsCount;
            },
            pageSize: docketRequest.pageSize,
            ajax: {
                beforeSend: function() {
                    //$('.search-result-summary').html('Loading search results...');
                }
            },
            callback: function(data, pagination) {
                renderResults(data, pagination);
            }
        });
    }
}

function renderResults(data, pagination) {
    let documentsTableBody = $('#documentsBody');

    if(pagination.totalNumber > 0) {
        documentsTableBody.find('tr:gt(0)').empty();

        $.each(data, function(i, result) {
            renderDocumentsResult(documentsTableBody, result);
        });

        documentsTableBody.find('tr:first').addClass('hide');
        $('.search-pagination').show();
    
    } else {
        documentsTableBody.find('tr:gt(0)').empty();
        documentsTableBody.find('tr:first').removeClass('hide');
        $('#documentsBody > tr:first > td').text('No records found');
        $('.search-pagination').hide();
    }
}

function renderDocumentsResult(documentsTableBody, result) {

    var url ='/search/facts-document/?documentId=' + result.documentId;

    var companyNames = [];
    
    $.each(result.companyDetailsVm, function(index, value){
        companyNames.push(value.companyName);
    });

    var attachmentClip =  "<div class='fas fa-paperclip no-paperclip'></div>";

    if(result.hasAttachment){
         attachmentClip = "<div class='fas fa-paperclip'></div>";
    }
    
    let searchResultContent =
        "<tr>" +
            "<td data-label='Document Id'>" +
            "<a href="+ url +">" +
                result.documentId +
            "</a>" +
            "</td>" +
            "<td data-label='Company'><a href="+ url +">" +
                companyNames.join(',') +
            "</a></td>" +
            "<td data-label='Filed'><a href="+ url +">" +
                result.filedDateString +
            "</a></td>" +
            "<td data-label='Received'><a href="+ url +">" +
                result.receivedDateString +
            "</a></td>" +
            "<td data-label='Description'><a href="+ url +">" +
                result.description +
            "</a></td>" +
            "<td data-label='Attachment'><a href="+ url +">" +
                attachmentClip +
            "</a></td>" +
        "</tr>";

    documentsTableBody.append(searchResultContent);
}

function SortColOnClick(){
    $(document).on('click', '.sort-col', function(){

        // hide 'a.sort-col-asc' and 'a.sort-col-desc' and unhide 'a.sort-col'
        var ob = $(this).parent().siblings().children('a.sort-col');
        for(var i=0; i< ob.length; i++)
        {
            $(ob[i]).addClass('hide');
            $(ob[i]).not('a.sort-col-asc').not('a.sort-col-desc').removeClass('hide');
        }

        $(this).addClass('hide');
        
        $('.search-pagination').hide();
        $('#documentsBody').find('tr:gt(0)').empty();
        $('#documentsBody').find('tr:first').removeClass('hide');
        $('#documentsBody > tr:first > td').text('Loading results...');

        // Sets the sort column
        docketRequest.sortColumn = $(this).parent().data('column-name');

        // Sets the sort direction
        var sortDirection = $(this).parent().data('column-sort-direction');
        if(sortDirection === "ASC") {
            $(this).parent().data('column-sort-direction', 'DESC')
            $(this).siblings('.sort-col-asc').removeClass('hide');
        }
        else {
            $(this).parent().data('column-sort-direction', 'ASC')
            $(this).siblings('.sort-col-desc').removeClass('hide');
        }

        docketRequest.sortDirection =  sortDirection;

        // Invoke API
        LoadDocumentsByDocketId(docketRequest, true, false);

    });
}

function PageSizeOnChange(){
    $(document).on('change', 'select#pageSize', function(){
        
        docketRequest.pageSize = $(this).val();

        var matchMediaQuery = window.matchMedia('(max-width: 640px)');

        if(matchMediaQuery != null ){
            if(matchMediaQuery.matches){
                LoadDocumentsByDocketId(docketRequest, false, true);
            }
            else{
                LoadDocumentsByDocketId(docketRequest, true, false);
            }
        }
        else{
            LoadDocumentsByDocketId(docketRequest, true, false);
        }
    });
}

function SearchTextOnKeyUp(){
    $(document).on('keyup', 'input#searchText', function(e){

        if(e.keyCode == 13){

            docketRequest.searchText = $(this).val();
            LoadDocumentsByDocketId(docketRequest, true, false);
        }
    });
}

function SearchTextClearOnClick(){
    $(document).on('click', '#clearField', function(){

        $('input#searchText').val('');
        docketRequest.searchText = '';

        LoadDocumentsByDocketId(docketRequest, true, false);
    });
}
