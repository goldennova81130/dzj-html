/**
 * Added by Zhang Yungui on 2018/12/18.
 */

function showError(title, text) {
  var $err = $('.ajax-error');
  if ($err.length === 1) {
    $err.text(text.replace(/[。！]$/, '')).show(200);
    return setTimeout(function () {
      $err.hide();
    }, 2000);
  }
  swal({
    title: title, text: text, type: /失败|错误/.test(title) ? 'error' : 'warning',
    timer: 2000, showConfirmButton: false
  });
}
function showSuccess(title, text) {
  swal({title: title, text: text, type: 'success', timer: 1000, showConfirmButton: false});
}

/**
 * 调用后端接口
 * @param url 以“/”开头的地址
 * @param type POST 或 GET
 * @param data 数据对象
 * @param success_callback 成功回调函数，参数为 data 对象或数组
 * @param error_callback 失败回调函数，参数为 msg、code
 */
function ajaxApi(url, type, data, success_callback, error_callback) {
  error_callback = error_callback || window.swal && function (msg) {
        showError('操作失败', msg);
      } || console.log.bind(console);

  if (data && typeof data.data === 'object') {
    data.data = JSON.stringify(data.data);
  }
  data = data || {};
  $.ajax({
    url: '/api' + url,
    data: $.param(data),
    dataType: 'json',
    type: type,
    xhrFields: {
      withCredentials: true
    },
    crossDomain: true,
    cache: false,
    success: function (data) {
      if (data.error) {
        error_callback(data.error, data.code);
      }
      else if (success_callback) {
        success_callback(data);
      }
    },
    error: function (xhr) {
      var code = xhr.status || xhr.code || 500;

      if (code >= 200 && code <= 299) {
        if (success_callback) {
          success_callback({});
        }
      }
      else if (!unloading) {
        error_callback('网络访问失败，不能访问后台服务(' + code + ')', code);
      }
    }
  });
}

/**
 * 以GET方式调用后端接口
 * @param url 以“/”开头的地址，不带 /api
 * @param success 成功回调函数，可选，参数为 data 对象或数组
 * @param error 失败回调函数，可选，参数为 msg、code
 */
function getApi(url, success, error) {
  ajaxApi(url, 'GET', null, success, error);
}

/**
 * 以POST方式调用后端接口
 * @param url 以“/”开头的地址，不带 /api
 * @param data 请求体JSON对象
 * @param success 成功回调函数，可选，参数为 data 对象或数组
 * @param error 失败回调函数，可选，参数为 msg、code
 */
function postApi(url, data, success, error) {
  ajaxApi(url, 'POST', data, success, error);
}

$.ajaxSetup({
  beforeSend: function (jqXHR, settings) {
    var type = settings.type;
    if (type !== 'GET' && type !== 'HEAD' && type !== 'OPTIONS') {
      var pattern = /(.+; *)?_xsrf *= *([^;" ]+)/;
      var xsrf = pattern.exec(document.cookie);
      if (xsrf) {
        jqXHR.setRequestHeader('X-Xsrftoken', xsrf[2]);
      }
    }
  }
});


var HTML_DECODE = {
  '&lt;': '<',
  '&gt;': '>',
  '&amp;': '&',
  '&nbsp;': ' ',
  '&quot;': '"'
};
// 将tornado在网页中输出的对象串转为JSON对象，toHTML为true时只做网页解码
function decodeJSON(s, toHTML) {
  s = s.replace(/&\w+;|&#(\d+);/g, function ($0, $1) {
    var c = HTML_DECODE[$0];
    if (c === undefined) {
      // Maybe is Entity Number
      if (!isNaN($1)) {
        c = String.fromCharCode(($1 === 160) ? 32 : $1);
      } else {
        // Not Entity Number
        c = $0;
      }
    }
    return c;
  });
  s = toHTML ? s : s.replace(/'/g, '"').replace(/: True/g, ': 1').replace(/: (False|None)/g, ': 0').replace(/\\/g, '/');
  return toHTML ? s : parseJSON(s);
}

function parseJSON(s) {
  try {
    return JSON.parse(s);
  }
  catch (e) {
    console.info('invalid JSON: ' + s);
  }
}
