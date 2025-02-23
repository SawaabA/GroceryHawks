function removePrevResults() {
    const cont = document.getElementById("results")
    if (cont) {
        cont.remove()
    }
}
async function fetchWorkOrders(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            const errorMessage = `Failed to fetch tracker data: ${response.statusText}`;
            console.error(errorMessage);
            throw new Error(errorMessage);
        }
        return await response.json();
    } catch (error) {
        console.error("Error in fetchWorkOrders:", error);
        throw error;
    }
}

function addLoadingBox() {
    const loadingBox = document.createElement('div');
    Object.assign(loadingBox.style, {
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        padding: '20px 40px',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        color: '#fff',
        fontSize: '18px',
        borderRadius: '8px',
        zIndex: '1000'
    });
    loadingBox.textContent = 'Loading...';
    const container = document.querySelector("main") || document.body;
    container.appendChild(loadingBox);
    return loadingBox;
}


function displayData(data) {
    const itemsContainer = document.createElement("ul")
    itemsContainer.classList.add('list-group')
    itemsContainer.id = "results"

    JSON.parse(data.result).forEach(itemData => {
        const listItem = document.createElement("li");
        listItem.className = "list-group-item d-flex align-items-center";
        listItem.innerHTML = `
        <div class="d-flex w-100">
            <div class="flex-shrink-0">
                <img src="${itemData.Image}" alt="${itemData.title}" class="rounded border img-fluid" style="width: 150px; height: 150px; object-fit: cover;">
            </div>
            <div class="ms-3 flex-grow-1">
                <div class="d-flex justify-content-between">
                    <h5 class="mb-0">${itemData.title}</h5>
                </div>
                <div class="container mt-4">
                    <div class="table-responsive">
                        <table class="table table-bordered table-striped text-center">
                            <thead>
                                <tr>
                                    <th><img width="100%" src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Walmart_logo.svg/200px-Walmart_logo.svg.png" alt="Walmart"></th>
                                    <th><img width="50%" src="https://seeklogo.com/images/Z/zehrs-markets-logo-D3A7CBE6BE-seeklogo.com.png" alt="Zehrs"></th>
                                    <th><img width="80%" src="https://freshco.com/wp-content/uploads/2020/11/freshco-logo-header.svg" alt="Freshco"></th>
                                    <th><img width="50%" src="https://upload.wikimedia.org/wikipedia/en/1/16/Food_Basics_Logo.png" alt="Food Basics"></th>
                                    <th><img width="100%" src="https://dis-prod.assetful.loblaw.ca/content/dam/loblaw-companies-limited/creative-assets/logos/pcx-banner-logos-/superstore_v2.svg" alt="Canadian Superstore"></th>
                                    <th><img width="50%" src="https://farahfoods.ca/cdn/shop/files/farahs_logo_smart_250x.png?v=1624062594" alt="Farahs"></th> <!-- Replace with actual logo -->
                                    <th><img width="100%"src="https://dis-prod.assetful.loblaw.ca/content/dam/loblaw-companies-limited/creative-assets/logos/pcx-banner-logos-/nofrills_v2.svg" alt="No Frills"></th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>${itemData.Walmart}</td>
                                    <td>${itemData.Zehrs}</td>
                                    <td>${itemData.Freshco}</td>
                                    <td>${itemData["Food Basics"]}</td >
                                    <td>${itemData["Canadian Superstore"]}</td>
                                    <td>${itemData.Farahs}</td>
                                    <td>${itemData["No Frills"]}</td>
                                </tr >
                            </tbody >
                        </table >
                    </div >
                </div >
            </div >
        </div > `;
        itemsContainer.appendChild(listItem);
    });

    document.querySelector("main").appendChild(itemsContainer)


}

async function submitSearch() {
    const loader = addLoadingBox();
    removePrevResults()
    const keyWordInput = document.getElementById("grocery-input").value;
    try {
        console.log("Searching for:", keyWordInput);
        const data = await fetchWorkOrders(`/search/${keyWordInput}`);
        displayData(data)
    } catch (error) {
        console.error("Error during search submission:", error);
    } finally {
        setTimeout(() => {
            loader.remove();
        }, 500);
    }
}
