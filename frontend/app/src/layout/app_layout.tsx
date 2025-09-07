import { Outlet } from "react-router-dom"
import { Link } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"


export default function AppLayout(){
      const [user, loading] = useAuth();
      console.log("Useer object is:", user)


      const links = [
            {path: "/", name: "Homepage"},
            ...(user ? 
                  [
                  {path: `/user/${user["uid"]}`, name: "Your Profile"},
                  {path: "/URLLink", name: "Shorten URL"},
                  ] : [
                        {path: `/auth`, name: "Log in / Register"},     
                  ]
            ),
            {path: "/Test", name: "Test"},
      ]
      return ( 
            <> 
            <div className="w-full h-screen"> 
                  <header id="header" 
                          className="w-full h-[10%] border-2 border-black flex items-center p-4">
                        <div id="company_info" className="h-max">
                              <p> URL SHORTENER</p>
                        </div>
                        <nav className="flex ml-auto gap-3">
                              {
                                   links.map((item, index) => (
                                    <Link key={index} to={item.path} className="btn-primary">{item.name}</Link>
                                   ))
                              }
                        </nav>
                  </header>
                  <main id="main-content" className="w-full h-[80%] p-2">
                        <Outlet />
                   </main>
                   <div id="footer" className="w-full h-[10%] border-2 border-black"> 
                        <p> This is my beatifu footer</p>
                   </div>
            </div>
            </>
      )
}