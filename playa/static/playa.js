if (Playa === undefined) {
    var Playa = {};
}
Playa.utils = {};
Playa.utils.duration = function(seconds){
    var minutes = parseInt(seconds / 60, 10);
    var seconds = ('0' + parseInt(seconds % 60, 10));
    seconds = seconds.substr(seconds.length - 2);
    return minutes + ':' + seconds;
};

Playa.player = function(){
    var self = this;
    
    this.init = function(){
        if ($('#now-playing')) {
            self.startTimer();
            var $vol = $('#now-playing .volume-bar');
            $vol.click(function(){
                var max = $vol.width();
                self.setVolume(event.offsetX / max);
            });

            var $seek = $('#now-playing .song-position');
            $seek.click(function(){
                var max = $seek.width();
                self.seek(event.offsetX / max);
            });
        }
    };
    
    this.fetch = function(){
        $.ajax({
            url: Playa.apiUrlMap.now_playing,
            dataType: 'json',
            success: self.update
        });
    };
    
    this.startTimer = function(){
        self.timer = setInterval(self.fetch, 500);
    };
    
    this.setVolume = function(value){
        $.ajax({
            type: 'POST',
            url: Playa.apiUrlMap.set_volume,
            dataType: 'json',
            data: {
                'value': value
            },
            success: function(data){
                $('#now-playing .volume-bar div').width(data.value + '%');
            }
        });
    };
    
    this.seek = function(value){
        $.ajax({
            type: 'POST',
            url: Playa.apiUrlMap.seek,
            dataType: 'json',
            data: {
                'pos': value
            },
            success: function(data){
                // $('#now-playing .volume-bar div').width(data.value + '%');
            }
        });
    };
    
    this.update = function(data){
         var $np = $('#now-playing');
         if (data.playing) {
             $np.find('.song-action a').removeClass('play-button').addClass('pause-button').html('Pause').attr('href', Playa.apiUrlMap.stop_playing);
         } else {
             $np.find('.song-action a').removeClass('pause-button').addClass('play-button').html('Play').attr('href', Playa.apiUrlMap.start_playing);
         }
         if (data.title) {
             $np.find('.song-name').html(data.title);
             $np.find('.song-pos').html('-' + Playa.utils.duration(data.duration - data.position));
             $np.find('.song-album').html(data.album || '');
             $np.find('.song-position div').css('width', (data.position / data.duration * 100) + '%');
         } else {
             $np.find('.song-name').html('');
             $np.find('.song-pos').html('');
             $np.find('.song-album').html('');
             $np.find('.song-position div').css('width', 0);
         }
    }
    
    $(this.init);
}();

$(function(){
    $('tbody tr').click(function(){
        var $this = $(this);
        var $cbx = $this.find('input[type=checkbox]');
        $cbx.attr('checked', !$cbx.is(':checked'));
    });
    $('thead input[type=checkbox]').change(function(){
        var $this = $(this);
        $this.parents('table').find('tbody tr input[type=checkbox]').attr('checked', $this.is(':checked'));
    });
});