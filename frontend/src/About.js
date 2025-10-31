import React from "react";

const skills = [
  "街舞", "Python", "Flask", "PostgreSQL", "Docker",  "popping", "Funk","React.js","CI/CD"
];

function About() {
  return (
    <div style={{
      maxWidth: 640,
      margin: "48px auto 0",
      background: "#fff",
      borderRadius: 20,
      boxShadow: "0 8px 32px #0001",
      padding: "40px 32px",
      textAlign: "center"
    }}>
      <img
        src="https://i.ibb.co/2YmvkczW/2025-07-18-225807.png"
        alt="Python 程式碼頭像"
        style={{
            width: 120,
            height: 120,
            borderRadius: "50%",
            border: "3px solid #FFD900",
            objectFit: "cover",
            marginBottom: 18,
            background: "#fff"
        }}
        />

      <h1 style={{
        fontSize: "2rem",
        letterSpacing: 2,
        marginBottom: 6,
        color: "#222"
      }}>Hi, 我是 Tsai B</h1>
      <div style={{
        color: "#888",
        fontSize: "1.1rem",
        marginBottom: 28
      }}>Graduated from the Institute of Information Management,<br /> National Cheng Kung University <br />Made of Funk, a street dance crew from Tainan</div>
      <div style={{
        fontSize: "1.08rem",
        lineHeight: 2.1,
        textAlign: "left",
        margin: "0 auto 28px",
        maxWidth: 460,
        color: "#444"
      }}>
        歡迎來到Raw type<br />
        這個網站是我自己設計的電商網站<br />
        後端使用Python Flask，前端使用React.js實作<br />
        除了網站是我自己設計的，網站上的衣服也是 !<br />
        我喜歡寫程式，享受開發從0到1的成就感。<br />
        除了coding之外，我也是一名街舞舞者<br />跳的舞風是popping，喜歡Funk音樂。<br />
        未來也希望能結合科技與興趣，創造更多有趣的專案。<br />
        Let’s make something nerdy and cool !
      </div>
      <div style={{
        display: "flex",
        flexWrap: "wrap",
        gap: 10,
        justifyContent: "center",
        marginBottom: 24
      }}>
        {skills.map(skill => (
          <span key={skill} style={{
            background: "#FFD900",
            color: "#222",
            borderRadius: 14,
            padding: "5px 16px",
            fontWeight: "bold",
            fontSize: "1rem",
            boxShadow: "0 1px 5px #0002",
            letterSpacing: 1
          }}>{skill}</span>
        ))}
      </div>
      <div style={{
        marginTop: 18,
        color: "#444",
        fontSize: "0.98rem"
      }}>
        Email: talen3031@gmail.com
      </div>
      <div style={{
            marginTop: 18,
            color: "#444",
            fontSize: "0.98rem"
            }}>
            GitHub: <a
                href="https://github.com/talen3031/Ecommerce"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#1890ff", textDecoration: "underline" }}
            >
                https://github.com/talen3031/Ecommerce
            </a>
            </div>
    </div>
    
  );
}

export default About;
