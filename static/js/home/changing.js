const letters = "abcdefghijklmnopqrstuvwxyz";
var posWords = ["striking", "advanced",
"artistic", "catching", "creative", "definite", "detailed",
"dominant", "dramatic", "engaging", "exciting", "familiar", "friendly", 
"historic", "official", "powerful", "precious", "pregnant",
"profound", "reliable", "romantic", "standard", "stunning", "suitable",
"superior", "sweeping", "tangible", "thorough", "touching",
"valuable", "holistic", "powerful", "charming"];

// Easter egg word in there ;)

function shuffle(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

shuffle(posWords); 

var interval = null;
var elem = document.getElementById("titleChanger");
var counter = 0;

elem.onmouseover = event => {  
    var iteration = 0;
    
    var word = posWords[counter];
    counter++;
    if(counter == posWords.length) {
        counter = 0;
    }
    
    clearInterval(interval);
    
    interval = setInterval(() => {
        var arr = elem.innerHTML.split("");
        var mapped = arr.map((letter, index) => {
            if(index < iteration) {
                return word[index];
            }
            
            return letters[Math.floor(Math.random() * 26)];
        });
        var joined = mapped.join("");
        elem.innerHTML = joined;
        
        if(iteration >= word.length) { 
            clearInterval(interval);
        }
        
        iteration += 1 / 3;
    }, 30);
}