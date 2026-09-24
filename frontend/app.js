const products = [
  ["Little Love Box", "₹199", "A purple box full of sweet little feelings.", "little-love-box.png"],
  ["Punny Love Cards", "₹179", "A cute card set for your favourite person.", "punny-love-cards.png"],
  ["Bloom Choco Notes", "₹199", "Floral notes with a chocolatey surprise.", "bloom-choco-notes.jpg"],
  ["Birthday Choco Board", "₹199", "A big, happy birthday in chocolates.", "birthday-choco-board.jpg"],
  ["Sweet Mini Cards", "₹159", "Tiny cards, tiny treats, huge smiles.", "sweet-mini-cards.jpg"],
  ["Earring Bouquet", "₹169", "A pretty little bouquet for a special pair.", "earring-bouquet.jpg"],
  ["Memory Love Bouquet", "₹399", "Photos, roses, and memories wrapped together.", "memory-love-bouquet.jpg"],
  ["Money Bloom Bouquet", "₹399–₹699", "A show-stopping bouquet made for celebrations.", "money-bloom-bouquet.png"],
  ["KitKat Ribbon Bar", "₹199", "Five sweet breaks, tied with a bow.", "kitkat-ribbon-bar.png"],
  ["Silk Surprise Bouquet", "₹219", "A purple silk-chocolate bouquet.", "silk-surprise-bouquet.jpg"],
  ["Midnight Silk Bouquet", "₹279", "Black, red, and silk chocolate magic.", "midnight-silk-bouquet.jpg"],
  ["Lavender Rose Pop", "₹99", "A tiny lavender rose with big charm.", "lavender-rose-pop.jpg"],
  ["Pink Rose Pop", "₹99", "A little pink rose, ready to gift.", "pink-rose-pop.jpg"],
].map(([name, price, caption, image]) => ({ name, price, caption, image: `assets/${image}` }));

const grid = document.querySelector("#product-grid");
const dialog = document.querySelector("#order-dialog");
const form = document.querySelector("#order-form");
const chosenProduct = document.querySelector("#chosen-product");
const productInput = document.querySelector("#product-input");
const status = document.querySelector("#form-status");

function renderProducts() {
  grid.innerHTML = products.map((product, index) => `
    <article class="product-card">
      <img class="product-image" src="${product.image}" alt="${product.name}" loading="lazy" />
      <div class="product-info">
        <div class="product-name-row"><h3 class="product-name">${product.name}</h3><strong class="product-price">${product.price}</strong></div>
        <p class="product-caption">${product.caption}</p>
        <button class="customize-button" data-product="${index}">Customise & order</button>
      </div>
    </article>`).join("");
}

grid.addEventListener("click", event => {
  const button = event.target.closest("[data-product]");
  if (!button) return;
  const product = products[Number(button.dataset.product)];
  form.reset();
  productInput.value = product.name;
  chosenProduct.innerHTML = `<span>${product.name}</span><strong>${product.price}</strong>`;
  status.textContent = "";
  dialog.showModal();
});

document.querySelector("#close-dialog").addEventListener("click", () => dialog.close());
dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });

form.addEventListener("submit", async event => {
  event.preventDefault();
  const submit = form.querySelector("button[type=submit]");
  submit.disabled = true;
  status.textContent = "Sending your request…";
  try {
    const response = await fetch("/api/orders", { method: "POST", body: new FormData(form) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Please try again.");
    status.textContent = "Request received! We’ll reply to your email soon.";
    form.reset();
  } catch (error) { status.textContent = error.message; }
  finally { submit.disabled = false; }
});

document.querySelector("#year").textContent = new Date().getFullYear();
renderProducts();
