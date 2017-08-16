//<%include file="/proto/common.js" />

function checkForException(data) {
    if (data.exception != undefined) {
        if (data.exception) {
            alert(data.exception);
            return true;
        }
    }
    return false;
}

var invalid = false;
var do_submit = false;

function setJobInfo(data) {
    var job_info = $('#job_info');
    if (job_info && data.job_info) {
        job_info.val(escape(data.job_info));
        $('#job_name').val(escape(data.job_name));
    }
}

function validate(f) {
    //alert('validate');
    //updateRunDescription(f);
    invalid = disableSubmit();
    //invalid = true;
    $('#validating').show();
    $.ajax({
        type:'post',
        dataType: 'json',
        url: '?mako=ajax&ajax=validate',
        data: $(f).serialize(),
        success: function (data) {
            checkForException(data);
            if (data.valid != 'OK') {
                invalid = true;
                //$('#start').attr('disabled', true);
                $('#status').html(data.valid);
                $('#status').show();
                //alert('validate:'+data);
                if (do_submit) {
                    do_submit = false;
                }
            } else {
                updateRunDescription(f);
                setJobInfo(data)
                invalid = false;
                $(f).attr('action', '${h.url_for("/tool_runner")}')
                $('#start').attr('disabled', false);
                $('#status').hide();
                $('#status').empty();
                if (do_submit) {
                    f.submit();
                }
            }
            restoreSubmit(invalid);
            $('#validating').hide();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //alert(textStatus + ': ' + errorThrown);
        }
    });
}

function setConfigChoices(f) {
    var href = '?mako=ajax&ajax=config';
    //alert(href);
    $.ajax({
        type: 'post',
        url: href,
        data: $(f).serialize(),
        dataType: 'json',
        success: function (data) {
            //alert(data.stats);
            checkForException(data);

            $('#stats').val(data.stats);
            $('#_stats_text').html(data.stats_text);
        }
    });
    updateRunDescription(f);
}

function getInfo(form, link, about) {
    var elem = $('#info_'+about);
    if (!$(link).hasClass('hideInfo')) {
        $('#show_info_'+about).val('1');
        var url = '?mako=ajax&ajax=trackinfo&about=' + escape($('#'+about).val());

        $.ajax({
            type: 'post',
            dataType: 'json',
            url: url,
            data: $(form).serialize(),
            success: function (data) {
                checkForException(data);
                //alert(data);
                elem.show();
                //elem.html(data);
                $(link).addClass('hideInfo');
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //alert(textStatus + ': ' + errorThrown);
            }
        });

    } else {
        $('#show_info_'+about).val('0');
        elem.hide();
        $(link).removeClass('hideInfo');
    }
}

function getGenomeInfo(form, link, genome) {
    var elem = $('#genome_info');
    if (!$(link).hasClass('hideInfo')) {
        $('#show_genome_info').val('1');
        var url = '?mako=ajax&ajax=genomeinfo&about=' + escape(genome);
        $.ajax({
            type: 'post',
            dataType: 'json',
            url: url,
            data: $(form).serialize(),
            success: function (data) {
                checkForException(data);
                //alert(data);
                elem.show();
                elem.html(data);
                $(link).addClass('hideInfo');
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //alert(textStatus + ': ' + errorThrown);
            }
        });
    } else {
        $('#show_genome_info').val('0');
        elem.hide();
        $(link).removeClass('hideInfo');
    }
}

function getHelp(about) {
    var elem = $('#help_'+about);
    elem.empty();
    if (elem.is(':visible')) {
        elem.hide();
        return;
    }
    var form = $('form');
    var url = '?mako=ajax&ajax=help&about=' + escape(about);
    $.ajax({
        type: 'post',
        dataType: 'json',
        url: url,
        data: form.serialize(),
        success: function (data) {
            checkForException(data);
            elem.html(data);
            elem.show();
            //$(link).addClass('hideInfo');
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //alert(textStatus + ': ' + errorThrown);
        }
    });
}

function hideHelp(about) {
    var elem = $('#help_'+about);
    elem.hide();
}

function getRunDescription(form, link, elem) {
    if (!$(link).hasClass('hideInfo')) {
        $('#showrundescription').val('1');
        var url = '?mako=ajax&ajax=rundescription&';
        $('#gettingrundescription').show();
        $.ajax({
            type: 'post',
            dataType: 'json',
            url: url,
            data: $(form).serialize(),
            success: function (data) {
                checkForException(data);
                //alert(data);
                $(elem).show();
                $(elem).html(data);
                $(link).addClass('hideInfo');
                $('#gettingrundescription').hide();
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                //alert(textStatus + ': ' + errorThrown);
            }
        });
    } else {
        $('#showrundescription').val('0');
        $(elem).hide();
        $(link).removeClass('hideInfo');
    }
}

function disableSubmit() {
    var old = $('#start').attr('disabled');
    if (!old) {
        $('#start').attr('disabled', true);
    }
    return old;
}

function restoreSubmit(old) {
    $('#start').attr('disabled', old);
}

function updateRunDescription(form) {
    if ($('#showrundescription').val() != '1') return;
    var elem = $('#rundescription');
    var url = '?mako=ajax&ajax=rundescription';
    //var submit = disableSubmit();
    $('#gettingrundescription').show();
    $.ajax({
        type: 'post',
        dataType: 'json',
        url: url,
        data: $(form).serialize(),
        success: function (data) {
            checkForException(data);
            //alert(data);
            //$(elem).show();
            $(elem).html(data);
            //$(link).addClass('hideInfo');
            //restoreSubmit(invalid);
            $('#gettingrundescription').hide();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            //alert(textStatus + ': ' + errorThrown);
        }
    });
}


function methodOnChange(self,event,updRunDescr) {
    var value = $(self).val();
        $('#pnl__brs__').hide();
        $('#pnl__chrs__').hide();
        $('#pnl__chrArms__').hide();
        $('#pnl__chrBands__').hide();
        $('#pnl__genes__').hide();
    switch (value) {
    case '__custom__':
        $('#pnlRegion').show();
        $('#pnlBinSize').show();
        $('#pnlChrArmNote').show();
        $('#pnlUserRegion').hide();
        break;
    case '__history__':
        $('#pnlRegion').hide();
        $('#pnlBinSize').hide();
        $('#pnlChrArmNote').hide();
        $('#pnlUserRegion').show();
        break;
    case '__brs__':
    case '__chrs__':
    case '__chrBands__':
        $('#pnlChrArmNote').show();
        $('#pnlRegion').hide();
        $('#pnlBinSize').hide();
        $('#pnlChrArmNote').show();
        $('#pnlUserRegion').hide();
        $('#pnl'+value).show();
        break;
    case '__chrArms__':
    case '__genes__':
        $('#pnlChrArmNote').show();
        $('#pnlRegion').hide();
        $('#pnlBinSize').hide();
        $('#pnlChrArmNote').hide();
        $('#pnlUserRegion').hide();
        $('#pnl'+value).show();
        break;
    default:
        $('#pnlRegion').hide();
        $('#pnlBinSize').hide();
        $('#pnlChrArmNote').hide();
        $('#pnlUserRegion').hide();
    }
    if (updRunDescr) {
        validate(self.form);
        //updateRunDescription(self.form);
    }
}

function optionOnClick(ev) {
    var opt = this;
    var id = '#' + opt.rel;
    $(id).val(opt.rev);
    $(id+'_text').val($(opt).text());
    $(id+'_display').text($(opt).text());
    $(id+'_options').hide();
    var onchange = $(id).attr('on_select');
    if (onchange) {
        //alert(onchange);
        eval(onchange);
    }
    with(document.forms['form']){action='';submit()}
    return false;
}

function optionsToggle(id) {
    var opts = $('#'+id+'_options');
    opts.toggle();
/*
    $('select').each(function (i) {
        var sel = $(this);
        if (sel.offset().top >= opts.offset().top) {
            sel.toggleClass('invisible');
        }
    });
*/
}

function checkNmerReload(event, element) {
    if (!element.value || element.value == '') {
        //element.value = '';
        //alert('Invalid nmer pattern');
        return;
    }
    if (event.type == 'blur' || event.keyCode == 13) {
        //if (! /[acgt]+/i.test(element.value)) {
        //    alert('Invalid nmer pattern');
        //    return;
        //}
        if (element.oldValue != element.value) {
            element.oldValue = element.value;
            element.form.action = '?';
            element.form.submit();
        }
    }
    element.oldValue = element.value;
}

function refreshOnChange(event, element) {
    if (!element.value || element.value == '') {
        return;
    }
disablePage();
    if (event.type == 'focus') {
        //element.submitState = disableSubmit();
        element.oldValue = element.value;
        //$(element.form).filter('input').attr('disabled', true);
    }
    if (event.type == 'blur') {
        if (element.oldValue != element.value) {
            element.oldValue = element.value;
            element.form.action = '?';
            element.form.submit();
        }
        //restoreSubmit(element.submitState);
    }
}

function resetAll() {
    if ($('#stats')) $('#stats').val('');
    if ($('#_stats')) $('#_stats').val('');
    if ($('#track1')) $('#track1').val('');
    if ($('#track2')) $('#track2').val('');
    if ($('#track3')) $('#track3').val('');
    if ($('#track1_0')) $('#track1_0').val('');
    if ($('#track2_0')) $('#track2_0').val('');
    if ($('#track3_0')) $('#track3_0').val('');
}

function setTrackToRecent(trackname, recent, form) {
    var rtrk = $(recent).val();
    $('#'+trackname).val(rtrk);
    $('#'+trackname+'_0').val(rtrk.split(':')[0]);
    form.action='?';
    form.submit()
}

function onSubmit(self) {
    disablePage();
    do_submit = true;
    validate(document.forms['form']);
    return false;
}

function appendValueFromInputToInput(from, to) {
    if (to.value) {
        to.value += ':' + from.value;
    } else {
        to.value = from.value;
    }
}

function main() {
    //$('.option').attr('href', 'javascript:;')
    $('.option').click(optionOnClick);

    //$('#method').change(methodOnChange);
    $('#method').change();
    $('#form').submit(onSubmit);

/*
    if (window.location.hash) {
        $(window.location.hash).focus();
    }
    if ($('#focused_element')) {
        var id = $('#focused_element').val();
        if (id)
            $('#' + id).focus();
    }
*/
}

$(document).ready(main);
