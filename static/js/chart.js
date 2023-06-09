function color_generator(opacidade = 1){
    let r = Math.random() * 255;
    let g = Math.random() * 255;
    let b = Math.random() * 255;

    if((r<100 && g<100 && b<100) || (r>180 && g>180 && b>180)){
        r = Math.random() * (180 - 100) + 100;
        g = Math.random() * (180 - 100) + 100;
        b = Math.random() * (180 - 100) + 100;
    };

    return `rgba(${r}, ${g}, ${b}, ${opacidade})`;
};

function unpack_list(list, key){
    aux = [];
    for(i=0;i<list.length;i++){
        aux.push(list[i][key]);
    };
    return aux;
};

function log_option(log){
    if(log){
        return {
            display: true,
            type: 'logarithmic',
            ticks: {
                beginAtZero: true,
                callback: function (value, index, values) {
                    return Number(value.toString());//pass tick values as a string into Number function
                }
            },
            afterBuildTicks: function (chartObj) { //Build ticks labelling as per your need
                chartObj.ticks = [];
                chartObj.ticks.push(0);
                chartObj.ticks.push(20);
                chartObj.ticks.push(40);
                chartObj.ticks.push(60);
                chartObj.ticks.push(80);
                chartObj.ticks.push(100);
                chartObj.ticks.push(1000);
                chartObj.ticks.push(2000);
                chartObj.ticks.push(3000);
            }
        }
    }
    return {
        display: true,
        ticks: {
            beginAtZero: true,
            stepSize: 1
        },
    }
}

function config_chart(log, legend, labels, ...args){
    var unpacked_args = [];

    for(i=0; i<args[0].length; i++){
        unpacked_args[i] = args[0][i];
    };

    function dataset(_args){
        dataset = []
        for (i=0;i<_args.length;i++){
            data = {
                label: legend[i],
                backgroundColor: color_generator(),
                data: _args[i],
            };
            dataset[i] = data;
        };
        return dataset;
    };

    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: dataset(unpacked_args),
        },
        options: {
            responsive: true,
            legend: {
                position: 'bottom',
            },
            scales: {
                yAxes: [log_option(log)]
            },
        }
    };
};

function create_dash(labels, legend, element, log_checkbox, ...args){
    ctx = document.getElementById(element).getContext('2d');
    return new Chart(ctx, config_chart(false, legend, labels, args));
};

function chartOptions(log){
    return {
        responsive: true,
        legend: {
            position: 'bottom',
        },
        scales: {
            yAxes: [log_option(log)]
        },
    };
};