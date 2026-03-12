// Einkaufsliste
function addItem() {
    const itemInput = document.getElementById('itemInput');
    const quantityInput = document.getElementById('quantityInput');
    const itemList = document.getElementById('itemList');

    if (itemInput.value.trim() !== '') {
        const li = document.createElement('li');
        li.textContent = `${itemInput.value} (Menge: ${quantityInput.value})`;

        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Entfernen';
        removeBtn.onclick = function () {
            itemList.removeChild(li);
        };

        li.appendChild(removeBtn);
        itemList.appendChild(li);

        itemInput.value = ''; // Feld zurücksetzen
        quantityInput.value = 1; // Menge zurücksetzen
    }
}

// To-Do-Liste
function addTask() {
    const taskInput = document.getElementById('taskInput');
    const taskList = document.getElementById('taskList');

    if (taskInput.value.trim() !== '') {
        const li = document.createElement('li');
        li.textContent = taskInput.value;

        const doneBtn = document.createElement('button');
        doneBtn.textContent = 'Erledigt';
        doneBtn.onclick = function () {
            li.style.textDecoration = 'line-through'; // Aufgabe als erledigt markieren
        };

        const removeBtn = document.createElement('button');
        removeBtn.textContent = 'Entfernen';
        removeBtn.onclick = function () {
            taskList.removeChild(li);
        };

        li.appendChild(doneBtn);
        li.appendChild(removeBtn);
        taskList.appendChild(li);

        taskInput.value = ''; // Feld zurücksetzen
    }
}
