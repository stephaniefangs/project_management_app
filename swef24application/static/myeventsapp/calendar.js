document.addEventListener("DOMContentLoaded", function () {
  var calendarEl = document.getElementById("calendar");
  var eventData = JSON.parse(document.getElementById("events-data").innerText);
  console.log(eventData);

  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay",
    },
    events: eventData,
    eventTimeFormat: {
        hour: 'numeric',
        minute: '2-digit',
        meridiem: 'short',
        hour12: true
    },
  });
  calendar.render();
});
