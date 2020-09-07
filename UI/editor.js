const pell = window.pell;
const markup = document.getElementById("markup");

const editor = pell.init({
  element: document.getElementById("editor"),
  onChange: (html) => {
    markup.innerHTML = "HTML Output: <br /><br />";
    markup.innerText += html;
  },
  actions: [
    'bold',
    'underline',
    {
      name: 'italic',
      result: () => pell.exec('italic')
    },
    {
      name: 'backColor',
      icon: '<div style="background-color:pink;">A</div>',
      title: 'Highlight Color',
      result: () => pell.exec('backColor', 'pink')
    },
    {
      name: 'image',
      result: () => {
        const url = window.prompt('Enter the image URL')
        if (url) pell.exec('insertImage', url)
      }
    },
    {
      name: 'link',
      result: () => {
        const url = window.prompt('Enter the link URL')
        if (url) pell.exec('createLink', url)
      }
    }
  ],
})
editor.content.innerHTML = `
    <div style="position:absolute;left:48px;top:105px;width:293px">
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt">Goal:</p>
        <p style="margin-top:0pt;margin-bottom:0pt">A Linux application that I can use to read and take notes</p>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt">Onenote seems to be all lightweight REST api calls.</p>
        <p style="margin-top:0pt;margin-bottom:0pt"><a href="https://msdn.microsoft.com/en-us/office/office365/howto/onenote-supported-ops">https://msdn.microsoft.com/en-us/office/office365/howto/onenote-supported-ops</a></p>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt">Steps to start:</p>
        <p style="margin-top:0pt;margin-bottom:0pt">A) Register</p>
        <p style="margin-top:0pt;margin-bottom:0pt">B) Authenticate</p>
        <p style="margin-top:0pt;margin-bottom:0pt">C) Simple client for view only </p>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt">Looks like a lot has been digested into Microsoft graph.</p>
        <p style="margin-top:0pt;margin-bottom:0pt"><a href="https://github.com/microsoftgraph/microsoft-graph-docs/blob/master/concepts/integrate_with_onenote.md">https://github.com/microsoftgraph/microsoft-graph-docs/blob/master/concepts/integrate_with_onenote.md</a></p>
        <p style="margin-top:0pt;margin-bottom:0pt"><a href="https://github.com/microsoftgraph/console-csharp-connect-sample">https://github.com/microsoftgraph/console-csharp-connect-sample</a></p>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt">There are three concepts:</p>
        <ol>
            <li style="list-style-type:lower-alpha">Onenote </li>
            <li style="list-style-type:lower-alpha">Onenote Page</li>
            <li style="list-style-type:lower-alpha">Onenote Page Content</li>
        </ol>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt">Starter:</p>
        <p style="margin-top:0pt;margin-bottom:0pt">Response:</p>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt"><a href="https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=543ead0b-cc06-487c-9b75-67213f2d5fff&amp;response_type=code&amp;redirect_uri=https%3A%2F%2Flogin.microsoftonline.com%2Fcommon%2Foauth2%2Fnativeclient&amp;response_mode=query&amp;scope=user.read%20notes.read">https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_id=543ead0b-cc06-487c-9b75-67213f2d5fff&amp;response_type=code&amp;redirect_uri=https%3A%2F%2Flogin.microsoftonline.com%2Fcommon%2Foauth2%2Fnativeclient&amp;response_mode=query&amp;scope=user.read%20notes.read</a></p>
        <br />
        <p style="margin-top:0pt;margin-bottom:0pt"><a href="https://login.microsoftonline.com/common/oauth2/nativeclient?code=Md6d374a2-ed35-4226-8d7c-c840a3e50936">https://login.microsoftonline.com/common/oauth2/nativeclient?code=Md6d374a2-ed35-4226-8d7c-c840a3e50936</a></p>
        <br />
        <img width="384" height="255.5" src="https://graph.microsoft.com/v1.0/users('antonydeepak@gmail.com')/onenote/resources/0-6ac31f2f65d246aeb020b9d3b19ecabe!1-F33E492FF42DEBDD!324082/$value" data-src-type="image/png" data-fullres-src="https://graph.microsoft.com/v1.0/users('antonydeepak@gmail.com')/onenote/resources/0-f7941c8bddba42b7821b42412f85487b!1-F33E492FF42DEBDD!324082/$value" data-fullres-src-type="image/jpeg" />
        <br />
    </div>
`