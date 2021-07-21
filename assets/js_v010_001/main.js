import "./crsf.js"
import { initCy } from "./graph.js"
import { makeMouseoverTippy } from "./iconsAndButtons.js";
import { showIntroTippy, toggleIntro } from "./intro.js";
import { logPageView, updateQuestionAnswerUsers } from "./utils.js";

logPageView();

const staticFileLocation = document.getElementById("static-root").getAttribute("data-name");

var graphP = fetch(`${staticFileLocation}positions_knowledge_graph_v010.json`).then(file => file.json());
var styleP = fetch(`${staticFileLocation}knowledge_graph.cycss`).then(file => file.text());

document.getElementById("shiprightButton").addEventListener("mouseover", makeMouseoverTippy("#shiprightButton", "Play your part in the future of Learney! We want to hear your thoughts and suggestions!"));
document.getElementById("slackButton").addEventListener("mouseover", makeMouseoverTippy("#slackButton", "Want to join the community or chat to us? Join our Slack and tell us!"));
// document.getElementById("feedbackButton").addEventListener("mouseover", makeMouseoverTippy("#feedbackButton", "Not a fan of Slack? Email us your feedback!"));

document.getElementsByClassName("profile-image")[0].onclick = function () {
    let profileDiv = document.getElementById("profile-div");
    if (profileDiv.style.display === "block") {
        profileDiv.style.display = "none";
    } else {
        profileDiv.style.display = "block";
    }
};

Promise.all([fetch(`${staticFileLocation}introSlides_v010.json`).then(file => file.json())]).then(
    function (slides) {
        let introSlides = slides[0];
        showIntroTippy(introSlides);
        document.getElementById("introButton").onclick = toggleIntro(introSlides);
    }
);

$(document).ready(function(){
    Promise.all([styleP, graphP]).then(initCy);
})

updateQuestionAnswerUsers();
