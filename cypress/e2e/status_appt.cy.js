describe("Update Status Appointment", () => {
    beforeEach(() => {
      cy.visit("/logout")
    })
    it("Should update appointment status to approve", () => {

        // Log in as a patient
        cy.visit('/login')
        cy.fixture("patient").then((patient) => {
            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()

            // Go to providers page
            cy.visit('/providers')
            cy.get("#id_name_query").type("TAMMY JONES", { log: false })
            cy.get("#id_state").select("WV")
            cy.get("#id_search").click()
            cy.get('ul.listing').find('li').first().find('a').first().click()
            cy.url().then(url => {
                cy.visit(url + '/schedule_appt')
            });

            // Schedule an appointment
            // Get the current date and time
            const now = new Date();
            now.setDate(now.getDate() + 2); // Add a day to the current date
            const currentDate = now.toISOString().split('T')[0]; // Format as YYYY-MM-DD
            const hrPad = now.getHours().toString().padStart(2, '0');
            const minPad = now.getMinutes().toString().padStart(2, '0');
            const currentTime = hrPad + ':' + minPad; // Format as HH:mm
            cy.get("#id_appointment_date").type(currentDate)
            cy.get("#id_appointment_time").type(currentTime)

            // Submit the form
            cy.get("#id_submit").click()

            // Assert that appointment was successfully requested
            cy.get('.messages').contains('Appointment requested successfully');
        })

        

        cy.visit("/logout")

        // Log in as a provider
        cy.visit('/login')
        cy.fixture("provider").then((provider) => {
            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password, { log: false })
            cy.get("#id_submit").click()

            // Go to the appointments page
            cy.visit('/profile/appointments')
            cy.get('h1').contains("Appointment List")
            cy.get('#appointment').find("li").first().click()
            cy.get('#approve-button').click()

            // Assert that appointment was successfully approved
            cy.get('#appointment-status').contains('Approved');
        })

        
    })
    it("Should update appointment status to reject", () => {
        // Log in as a patient
        cy.visit('/login')
        cy.fixture("patient").then((patient) => {
            cy.get("#id_email").type(patient.username)
            cy.get("#id_password").type(patient.password, { log: false })
            cy.get("#id_submit").click()
        })

        // Go to providers page
        cy.visit('/providers')
        cy.get("#id_name_query").type("TAMMY JONES", { log: false })
        cy.get("#id_state").select("WV")
        cy.get("#id_search").click()
        cy.get('ul.listing').find('li').first().find('a').first().click()
        cy.url().then(url => {
            cy.visit(url + '/schedule_appt')
        });

        // Schedule an appointment
        // Get the current date and time
        const now = new Date();
        now.setDate(now.getDate() + 1); // Add a day to the current date
        const currentDate = now.toISOString().split('T')[0]; // Format as YYYY-MM-DD
        const hrPad = now.getHours().toString().padStart(2, '0');
        const minPad = now.getMinutes().toString().padStart(2, '0');
        const currentTime = hrPad + ':' + minPad; // Format as HH:mm
        cy.get("#id_appointment_date").type(currentDate)
        cy.get("#id_appointment_time").type(currentTime)

        // Submit the form
        cy.get("#id_submit").click()

        // Assert that appointment was successfully requested
        cy.get('.messages').contains('Appointment requested successfully');

        cy.visit("/logout")

        // Log in as a provider
        cy.visit('/login')
        cy.fixture("provider").then((provider) => {
            cy.get("#id_email").type(provider.username)
            cy.get("#id_password").type(provider.password, { log: false })
            cy.get("#id_submit").click()
        })

        // Go to the appointments page
        cy.visit('/profile/appointments')
        cy.get('h1').contains("Appointment List")
        cy.get('#appointment').find("li").eq(1).click() // Select the second appointment
        cy.get('#reject-button').click()

        // Assert that appointment was successfully rejected
        cy.get('#appointment-status').contains('Rejected');
    })
})