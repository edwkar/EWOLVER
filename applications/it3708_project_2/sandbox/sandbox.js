/* vim: set ts=2 sw=2 tw=100: */

$(document).ready(function(){

var arraysEqual = function(a,b) { return !(a<b || b<a); };

var izhikevichTest = (function(){ 
  var __c_izhikevichTest = Module.cwrap('izhikevichTest', 'number', 
              ['number', 'number', 'number', 'number', 'number', 
               'number', 'number', 'number', 'number', 'number']);

  return function() {
    var tPre = Date.now();
    __c_izhikevichTest.apply(null, arguments);
    return {
      firstPotentials: __NEURON_A_POTENTIALS,
      firstSpiketimes: __NEURON_A_SPIKE_TIMES,

      secondPotentials: __NEURON_B_POTENTIALS,
      secondSpiketimes: __NEURON_B_SPIKE_TIMES
    };
  };
})();

var neuronNames = ['orange', 'green'];
var paramNames = ['a', 'b', 'c', 'd', 'k'];

var fetchData = function(){
  var args = [];
  neuronNames.forEach(function(neuronName){
    paramNames.forEach(function(paramName){
      var v = parseFloat($('#' + neuronName + '_' + paramName).val());
      if (Math.abs(v) < 1e-6)
        v = 1e-6;
      args.push(v);
    });
  });

  var data = izhikevichTest.apply(null, args);
  var aPots = [];
  var bPots = [];
  for (var i = 0; i < data.firstPotentials.length; ++i) {
    aPots.push([i, data.firstPotentials[i]]);
    bPots.push([i, data.secondPotentials[i]]);
  }

  return {
    plots: [aPots, bPots]
  };
};

var plot = $.plot("#plot", fetchData().plots, {
  series: { shadowSize: 0 },
  yaxis: { min: -100, max: 100 },
  xaxis: { show: false },
  colors: ['#ff5555', '#55ff55'],
  grid: {
    backgroundColor: '#222222'
  }
});

var lastInputTime = Date.now(),
    lastRedrawTime = lastInputTime-42;
var update = function() {
  if (lastRedrawTime < lastInputTime) {
    lastRedrawTime = Date.now();
    var data = fetchData();
    plot.setData(data.plots);
    plot.draw();
  }
  $('#analysis').html(__ANALYSIS.replace(/\/N/g, '<br />'));
  setTimeout(update, 20);
};

$('input').keydown(function(event) {
  var d;
  if (event.which == 40) 
    d = -0.005;
  else if (event.which == 38) 
    d = 0.005; 
  else
    return;

  var v = parseFloat($(event.target).val());
  if (Math.abs(v) >= 10)
    d *= 10;
  if (Math.abs(v) <= 0.1)
    d /= 10.0;
  $(event.target).val((v + d).toFixed(4));
});

var copyParams = function(a, b) {
  paramNames.forEach(function(paramName){
    $('#' + a + '_' + paramName).val($('#' + b + '_' + paramName).val());
  });
  lastInputTime = Date.now();
};

$('#copy_from_green').click(function(){ copyParams('orange', 'green'); });
$('#copy_from_orange').click(function(){ copyParams('green', 'orange'); });

$(document).keyup(function() { lastInputTime = Date.now(); });


update();

});
