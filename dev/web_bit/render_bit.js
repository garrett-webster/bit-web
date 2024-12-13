let currentTab = null;
let currentIndex = {};

function createTabs() {
    const tabsContainer = document.getElementById('tabs');
    tabsContainer.innerHTML = ''; // Clear existing tabs
    Object.keys(data).forEach(key => {
        const tabButton = document.createElement('button');
        tabButton.innerText = key;
        tabButton.className = 'tab-button';
        if (key === currentTab) {
            tabButton.classList.add('active');
        }
        tabButton.onclick = () => switchTab(key);
        tabsContainer.appendChild(tabButton);
        currentIndex[key] = 0;
    });

    if (!currentTab) {
        currentTab = Object.keys(data)[0];
        switchTab(currentTab);
    }

    const firstButton = document.createElement('button');
    firstButton.innerText = 'First';
    firstButton.classList.add('button');
    firstButton.onclick = () => {
        currentIndex[currentTab] = 0;
        renderWorld();
    };

    const prevButton = document.createElement('button');
    prevButton.innerText = 'Previous';
    prevButton.classList.add('button');
    prevButton.onclick = () => {
        if (currentIndex[currentTab] > 0) {
            currentIndex[currentTab]--;
            renderWorld();
        }
    };

    const nextButton = document.createElement('button');
    nextButton.innerText = 'Next';
    nextButton.classList.add('button');
    nextButton.onclick = () => {
        if (currentIndex[currentTab] < data[currentTab].length - 1) {
            currentIndex[currentTab]++;
            renderWorld();
        }
    };

    const lastButton = document.createElement('button');
    lastButton.innerText = 'Last';
    lastButton.classList.add('button');
    lastButton.onclick = () => {
        currentIndex[currentTab] = data[currentTab].length - 1;
        renderWorld();
    };

    // TODO - add jump buttons

    const buttonContainer = document.getElementById('button-container');
    buttonContainer.innerHTML = '';
    buttonContainer.appendChild(firstButton);
    buttonContainer.appendChild(prevButton);
    buttonContainer.appendChild(nextButton);
    buttonContainer.appendChild(lastButton);
}

function switchTab(tab) {
    currentTab = tab;
    const tabsContainer = document.getElementById('tabs');
    Array.from(tabsContainer.children).forEach(button => {
        button.classList.remove('active');
        if (button.innerText === tab) {
            button.classList.add('active');
        }
    });
    renderWorld();
}

function renderWorld() {
    const worldContainer = document.getElementById('world-container');
    worldContainer.innerHTML = '';
    const worldData = data[currentTab][currentIndex[currentTab]].world;
    const pos = data[currentTab][currentIndex[currentTab]].pos;
    const orientation = data[currentTab][currentIndex[currentTab]].orientation;
    const grid = document.createElement('div');
    grid.className = 'grid';
    grid.style.gridTemplateColumns = `repeat(${worldData[0].length}, 50px)`;
    grid.style.gridTemplateRows = `repeat(${worldData.length}, 50px)`;
    for (let row = worldData.length - 1; row >= 0; row--) {
        for (let col = 0; col < worldData[row].length; col++) {
            const cellColor = worldData[row][col];
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.style.backgroundColor = cellColor;
            if (row === pos[0] && col === pos[1]) {
                const triangle = document.createElement('div');
                triangle.className = 'triangle';
                switch (orientation) {
                    case 0:
                        triangle.classList.add('right');
                        break;
                    case 1:
                        triangle.classList.add('up');
                        break;
                    case 2:
                        triangle.classList.add('left');
                        break;
                    case 3:
                        triangle.classList.add('down');
                        break;
                }
                cell.appendChild(triangle);
            }
            grid.appendChild(cell);
        }
    }
    worldContainer.appendChild(grid);
}

// if (hasSnapshots) {
//     const prevSnapClick = () => {
//         history = data[currentTab];
//         const snapshots = history.slice(0, currentIndex).map((event, pos) => {
//             if (event.name.startsWith('snapshot')) {
//                 return pos;
//             }
//         }).filter(pos => pos !== undefined);
//         currentIndex = snapshots.length ? snapshots[snapshots.length - 1] : 0;
//     };
//
//     const prevSnapButton = document.createElement('button');
//     prevSnapButton.innerText = "<< Jump";
//     prevSnapButton.onclick = prevSnapClick;
// }

function render() {
    // data = JSON.parse(bit_results);
    if (Object.keys(data).length === 0) {
        return;
    }
    createTabs();
    renderWorld();
}

