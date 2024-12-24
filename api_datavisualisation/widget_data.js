
// widget route_point

function route_point(container,graph) {
    return api.csv(graph, {}).then((data)
        => {route_point_render(container,data);

});

}



function route_point_render(container,data) {
let top_zone = $("<div class='cgn-service-route cgn-table-card d-flex cgn-card flex-column cgn-table-overflow'></div>");

container.append(top_zone);
let title_card = $("<h1 class='w-auto'>"+
$.i18n('selected_pathway')+"</h1>");
top_zone.append(title_card);

data.forEach(stop => {
    const stopElement = document.createElement("div");
    stopElement.classList.add("selected");
    stopElement.innerHTML
    = `
        <div>${stop.boarding};${stop.alighting}<br>${stop.load}</div>
        <div> ${stop.stop_name}<br>${stop.stop_id}</div>`;
top_zone.append(stopElement);
}); 
}

// widget route_exploitation

function 
route_exploitation(container ,graph) {
        return api.csv(graph, {}).then((data)
        => { route_exploitation_render(container ,graph, data);
    });
}

function route_exploitation_render(container ,graph, data) {
let top_zone = $("<div class='cgn-card cgn-table-card d-flex flex-column cgn-table-overflow'></div>");
container.append(top_zone);

// create table
let table = $("<table data-title="
    + `graph.${graph.id}.title`
    + "'class='table table-hover' style='margin-bottom: 0'></table>");

let thead = document.createElement('thead');
let tbody = document.createElement('tbody');

table.append(thead, tbody); 
top_zone.append(table);
thead.innerHTML
    = 
        `<tr>
            <th style="text-align: left;">Field</th>
            <th style="text-align: left;">Value</th>
        </tr> `;

// button definition

const button = document.createElement('button');
button.textContent = "Les caractéristiques d'une course";

top_zone.prepend(button);
data.forEach((item) => {let row
        = document.createElement('tr');

// define cell for item.fields

let tdField = document.createElement('td');

tdField.setAttribute('data-value', item.fields);
tdField.textContent = item.fields;

// define cell for pour item.values

let tdValue = document.createElement('td');

tdValue.setAttribute('data-value',item.values);
tdValue.textContent = item.values;

row.append(tdField);
row.append(tdValue);
tbody.append(row);
});
}


