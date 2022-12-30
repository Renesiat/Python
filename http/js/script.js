document.addEventListener('DOMContentLoaded', () => {
  const authButton = document.querySelector("#auth-button");
  if( ! authButton ) throw "DOMContentLoaded: #auth-button not found" ;
  authButton.addEventListener('click', authButtonClick ) ;

  const itemsButton = document.querySelector("#items-button");
  if( ! itemsButton ) throw "DOMContentLoaded: #items-button not found" ;
  itemsButton.addEventListener('click', itemsButtonClick ) ;
});
function itemsButtonClick(e) {
  const accessToken = window.sessionStorage.getItem("access_token");
  if( ! accessToken ) {
      alert( "Необхідно авторизуватись" );
      return ;
  }
  fetch( "/items", {
      method: "GET",
      headers: {
          "Authorization": "Bearer " + accessToken 
      }
  }).then( r => {
      if( r.status != 200 ) {
          out.innerText = "Контент заблоковано. Можливо помилка авторизації";
      }
      else {
          out.innerText = "Контент буде тут" ;
      }
  } ) ;
}
function authButtonClick(e) {
  const userLogin = document.querySelector("#user-login");
  if( ! userLogin ) throw "authButtonClick: #user-login not found" ;
  const userPassword = document.querySelector("#user-password");
  if( ! userPassword ) throw "authButtonClick: #user-password not found" ;
  // TODO: перевірити на заповненість та формат
  const credentials = btoa( userLogin.value + ":" + userPassword.value ) ;
  fetch( "/auth", {
      method: "GET",
      headers: {
          "Authorization": "Basic " + credentials
      }
  }).then( r => {
      if( r.status == 401 ) {
          r.text().then( t => out.innerText = t ) ;
      }
      else if( r.status == 200 ) {
          r.text().then( j => {
              out.innerText = j;//.access_token;
              // window.sessionStorage.setItem('access_token', j.access_token);
          });
      }
  })
}